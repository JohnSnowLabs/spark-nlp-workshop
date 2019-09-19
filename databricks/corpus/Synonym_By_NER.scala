// Databricks notebook source
import org.apache.spark.sql._
import org.apache.spark.sql.functions.{desc, col, count, sum, lower, regexp_replace}

// COMMAND ----------

// MAGIC %md ### The idea of this notebook is to have a dataset like this:
// MAGIC [icd10cm_ner, substr_to_replace, s2r_synonym]

// COMMAND ----------

def rrf2parquet(file: String, table_name: String, sep: String, headers: Seq[String]): DataFrame = {
  val rels = spark.read.format("csv").option("sep", sep).load(file).toDF(headers:_*)
  print(rels.columns)
  rels.write.mode("overwrite").format("parquet").option("quote",'"').saveAsTable(table_name)
  spark.sql("select * from "+table_name)
}

// COMMAND ----------

// MAGIC %md In case the table is a new one import it and put it in parquet

// COMMAND ----------

//val cuis = rrf2parquet("/andres/umls/data/MRCONSO.RRF","umls.mrconso","|",Seq("CUI","LAT","TS","LUI","STT","SUI","ISPREF","AUI","SAUI","SCUI","SDUI","SAB","TY","CODE","STR","SRL","SUPPRESS","CVF","discard"))
//val rels = rrf2parquet("/andres/umls/data/MRREL.RRF","umls.mrrel","|",Seq("CUI1","AUI1","STYPE1","REL","CUI2","AUI2","STYPE2","RELA","RUI","SRUI","SAB","SL","RG","DIR","SUPPRESS","CVF","discard"))
//val styp = rrf2parquet("/andres/umls/data/MRSTY.RRF","umls.mrsty","|",Seq("CUI","TUI","STN","STY","ATUI","CVF","discard"))
//val ners = rrf2parquet("/andres/icd10/icd10cm_ners.csv","icd10.ners", ",", Seq("code", "ner_chunk", "tokens"))

// COMMAND ----------

ners_array.select("code", "ner_chunk_").orderBy("code").limit(100).show(false)

// COMMAND ----------

// MAGIC %md Otherwise load them from disk

// COMMAND ----------

val cuis = spark.sql("select cui, lower(str) as str from umls.mrconso").distinct() // Concepts from UMLS
val rels = spark.sql("select cui1, cui2, rel from umls.mrrel") // Relationships between CUIs
val ners = spark.sql("select code, explode(ner) as ner from icd10.ners_by_code").select(col("code"), lower(col("ner")).alias("ner")).groupBy("ner").count() // NERs from ICD10 using clinical NER
//val ners = spark.sql("select * from icd10.ners").groupBy("ner").count() // NERs from ICD10 using clinical NER

// COMMAND ----------



// COMMAND ----------

// MAGIC %md Let's first try to cover as many ICD10 recognized entities as possible with CUIs

// COMMAND ----------

val cuis_sub_1 = ners.join(cuis, ners("ner")===cuis("str")).withColumn("original_ner",col("ner"))
val not_cuis_sub_1 = ners.join(cuis_sub_1.select("original_ner"), ners("ner")===col("original_ner"), "leftouter").where("original_ner is null").select(col("ner").alias("original_ner"),col("ner"), col("count"))

// COMMAND ----------

println(ners.count(), ners.agg(sum("count")).head(1)(0))
println(cuis_sub_1.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))
println(not_cuis_sub_1.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))

// COMMAND ----------

not_cuis_sub_1.orderBy(desc("count")).show(100,false)

// COMMAND ----------

val regexp_2 = "(unspecified\\s*|other\\s*|\\s*affected|current\\s*|\\bthe\\s*|\\bits\\s*)"
val ners_left_1 = not_cuis_sub_1.select(regexp_replace(col("ner"), regexp_2, "").alias("ner"),col("original_ner"),col("count"))
val cuis_sub_2 = ners_left_1.join(cuis, col("ner")===col("str"))
val not_cuis_sub_2 = ners_left_1.join(cuis_sub_2.select("cui","ner"), ners_left_1("ner")===cuis_sub_2("ner"), "leftouter").where("cui is null").select(ners_left_1("original_ner"), ners_left_1("ner"), ners_left_1("count"))

// COMMAND ----------

println(cuis_sub_2.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))
println(not_cuis_sub_2.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))

// COMMAND ----------

not_cuis_sub_2.orderBy(desc("count")).show(100,false)

// COMMAND ----------

// TODO: Instead of replacing these with empty string, split and explode
val regexp_3 = "(\\s+in\\s+.{0,}|\\s+of\\s+.{0,}|\\s+type\\s+.{0,}|\\s+\\d+$)"
val ners_left_2 = not_cuis_sub_2.select(regexp_replace(col("ner"), regexp_3, "").alias("ner"),col("original_ner"),col("count"))
val cuis_sub_3 = ners_left_2.join(cuis, col("ner")===col("str"))
val not_cuis_sub_3 = ners_left_2.join(cuis_sub_3.select("cui","ner"), ners_left_2("ner")===cuis_sub_3("ner"), "leftouter").where("cui is null").select(ners_left_2("original_ner"), ners_left_2("ner"), ners_left_2("count"))

// COMMAND ----------

println(cuis_sub_3.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))
println(not_cuis_sub_3.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))

// COMMAND ----------

not_cuis_sub_3.orderBy(desc("count")).show(100,false)

// COMMAND ----------

val manual_sub = spark.createDataFrame(Seq(
  ("C0043240","healing","routine healing","healing",2504),
  ("C0480203","self inflicted injury","intentional self-harm","intentional self-harm",1035),
  ("C0549152","nail damage","damage to nail","damage to nail",850),
  ("C1112363","underdose","underdosing","underdosing",264)
)).toDF("cui","str","original_ner","ner","count")

// COMMAND ----------

val cols = Array("cui","str","original_ner","ner","count")
val all_sub = cuis_sub_1.selectExpr(cols: _*)
.union(cuis_sub_2.selectExpr(cols: _*))
.union(cuis_sub_3.selectExpr(cols: _*))
.union(manual_sub.selectExpr(cols: _*))
.distinct()
.cache()

// COMMAND ----------

println(all_sub.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))

// COMMAND ----------

all_sub.where("original_ner!=ner").select("ner","cui","count").distinct().orderBy(desc("count")).show(50,false)

// COMMAND ----------

all_sub.select("ner","cui").distinct().groupBy("ner").count().orderBy(desc("count")).show(100, false)

// COMMAND ----------

val syn_half_1 = all_sub.join(rels,all_sub("cui")===rels("cui1")).where("rel='SY'")
val syn_half_2 = all_sub.join(rels,all_sub("cui")===rels("cui2")).where("rel='SY'")
val syn_pre = syn_half_1.selectExpr(syn_half_1.columns: _*).union(syn_half_2.selectExpr(syn_half_1.columns: _*)).distinct()

// COMMAND ----------

val syns = syn_pre.join(cuis.select(col("cui").alias("syncui"),col("str").alias("synonym")).alias("syncuis"), rels("cui2")===col("syncui") && syn_pre("ner")!=col("synonym")).distinct().cache()

// COMMAND ----------

println(all_sub.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))
println(syn_pre.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))
println(syns.select("original_ner","ner","count").distinct().agg(count("count"),sum("count")).head(1)(0))

// COMMAND ----------

syns.select("original_ner","ner","synonym").distinct().show(1000,false)

// COMMAND ----------

syns.where("ner like '%pressure%ulcer%' and synonym like '%bed%'").select("ner","str","synonym").distinct().show()

// COMMAND ----------

syns.groupBy("str","original_ner","ner","synonym").count().orderBy(desc("count")).show(1000,false)

// COMMAND ----------

syns.write.format("parquet").saveAsTable("icd10.synonyms_by_ner")

// COMMAND ----------



// COMMAND ----------


