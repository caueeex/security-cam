"""
Spark job para processamento de dados de segurança
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json
from datetime import datetime, timedelta

def create_spark_session():
    """Criar sessão Spark"""
    return SparkSession.builder \
        .appName("SecurityCamDataProcessing") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def process_detection_data(spark, input_path, output_path):
    """Processar dados de detecção"""
    
    # Ler dados de detecção
    detections_df = spark.read \
        .option("multiline", "true") \
        .json(input_path)
    
    # Processar dados
    processed_df = detections_df \
        .withColumn("date", to_date(col("frame_timestamp"))) \
        .withColumn("hour", hour(col("frame_timestamp"))) \
        .withColumn("risk_score", 
            when(col("risk_level") == "critical", 4)
            .when(col("risk_level") == "high", 3)
            .when(col("risk_level") == "medium", 2)
            .otherwise(1)
        ) \
        .withColumn("is_verified", col("is_verified").cast(BooleanType())) \
        .withColumn("is_false_positive", col("is_false_positive").cast(BooleanType()))
    
    # Agregações por hora
    hourly_stats = processed_df \
        .groupBy("date", "hour", "camera_id") \
        .agg(
            count("*").alias("total_detections"),
            sum(when(col("is_verified"), 1).otherwise(0)).alias("verified_detections"),
            sum(when(col("is_false_positive"), 1).otherwise(0)).alias("false_positives"),
            avg("confidence_score").alias("avg_confidence"),
            avg("risk_score").alias("avg_risk_score"),
            countDistinct("detection_type").alias("unique_detection_types")
        )
    
    # Salvar resultados
    hourly_stats.write \
        .mode("overwrite") \
        .parquet(output_path + "/hourly_stats")
    
    return hourly_stats

def process_alert_data(spark, input_path, output_path):
    """Processar dados de alerta"""
    
    # Ler dados de alerta
    alerts_df = spark.read \
        .option("multiline", "true") \
        .json(input_path)
    
    # Processar dados
    processed_df = alerts_df \
        .withColumn("date", to_date(col("created_at"))) \
        .withColumn("hour", hour(col("created_at"))) \
        .withColumn("priority_score",
            when(col("priority") == "critical", 4)
            .when(col("priority") == "high", 3)
            .when(col("priority") == "medium", 2)
            .otherwise(1)
        ) \
        .withColumn("resolution_time_minutes",
            when(col("resolved_at").isNotNull(),
                (unix_timestamp(col("resolved_at")) - unix_timestamp(col("created_at"))) / 60
            ).otherwise(None)
        )
    
    # Agregações por hora
    hourly_alerts = processed_df \
        .groupBy("date", "hour", "camera_id") \
        .agg(
            count("*").alias("total_alerts"),
            sum(when(col("status") == "pending", 1).otherwise(0)).alias("pending_alerts"),
            sum(when(col("status") == "resolved", 1).otherwise(0)).alias("resolved_alerts"),
            avg("priority_score").alias("avg_priority"),
            avg("resolution_time_minutes").alias("avg_resolution_time")
        )
    
    # Salvar resultados
    hourly_alerts.write \
        .mode("overwrite") \
        .parquet(output_path + "/hourly_alerts")
    
    return hourly_alerts

def generate_anomaly_report(spark, detections_path, alerts_path, output_path):
    """Gerar relatório de anomalias"""
    
    # Ler dados processados
    detections = spark.read.parquet(detections_path + "/hourly_stats")
    alerts = spark.read.parquet(alerts_path + "/hourly_alerts")
    
    # Join dos dados
    combined_data = detections.join(alerts, ["date", "hour", "camera_id"], "outer") \
        .fillna(0, subset=["total_detections", "total_alerts"])
    
    # Calcular métricas de anomalia
    anomaly_report = combined_data \
        .withColumn("detection_rate", col("total_detections") / 60) \
        .withColumn("alert_rate", col("total_alerts") / 60) \
        .withColumn("false_positive_rate", 
            when(col("total_detections") > 0, col("false_positives") / col("total_detections"))
            .otherwise(0)
        ) \
        .withColumn("anomaly_score",
            (col("detection_rate") * 0.3) + 
            (col("alert_rate") * 0.4) + 
            (col("false_positive_rate") * 0.3)
        )
    
    # Identificar períodos anômalos
    anomaly_periods = anomaly_report \
        .filter(col("anomaly_score") > 0.7) \
        .orderBy(desc("anomaly_score"))
    
    # Salvar relatório
    anomaly_periods.write \
        .mode("overwrite") \
        .parquet(output_path + "/anomaly_report")
    
    return anomaly_periods

def main():
    """Função principal"""
    
    # Criar sessão Spark
    spark = create_spark_session()
    
    # Configurações
    input_base_path = "s3a://security-cam-data/raw"
    output_base_path = "s3a://security-cam-data/processed"
    
    try:
        # Processar dados de detecção
        print("Processando dados de detecção...")
        detections_stats = process_detection_data(
            spark, 
            input_base_path + "/detections", 
            output_base_path
        )
        
        # Processar dados de alerta
        print("Processando dados de alerta...")
        alerts_stats = process_alert_data(
            spark, 
            input_base_path + "/alerts", 
            output_base_path
        )
        
        # Gerar relatório de anomalias
        print("Gerando relatório de anomalias...")
        anomaly_report = generate_anomaly_report(
            spark,
            output_base_path,
            output_base_path,
            output_base_path
        )
        
        print("Processamento concluído com sucesso!")
        
        # Mostrar estatísticas
        print(f"Total de registros de detecção processados: {detections_stats.count()}")
        print(f"Total de registros de alerta processados: {alerts_stats.count()}")
        print(f"Períodos anômalos identificados: {anomaly_report.count()}")
        
    except Exception as e:
        print(f"Erro no processamento: {e}")
        raise
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
