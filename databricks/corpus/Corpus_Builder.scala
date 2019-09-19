// Databricks notebook source
import org.apache.spark.sql.functions._

// COMMAND ----------

// Read the ICD10CM joined to NER_by_Code and Synonyms_by_NER and Semantic Type 

// COMMAND ----------

val rootDS = spark.sql("""select distinct code, description, sbn.original_ner, lower(a.ner) ner, sbn.synonym, mrsty.sty
from 
  (select cm.code, cm.description, explode(ner) ner 
  from icd10.icd10cm cm 
  join icd10.ners_by_code nbc 
  on cm.code=nbc.code) a
left join icd10.synonyms_by_ner sbn
on lower(a.ner)=lower(sbn.ner)
left join umls.mrsty mrsty
on sbn.cui=mrsty.cui""")

// COMMAND ----------

val tupleDS=rootDS.withColumn("NERSYN", array(rootDS("ner"), rootDS("synonym")))

// COMMAND ----------

val nerSyns = collect_set(tupleDS("NERSYN")).alias("NERSYN")
val nerSet = collect_set(tupleDS("ner")).alias("ner")
val nerStype = collect_set(tupleDS("sty")).alias("sty")
val groupedTuples = tupleDS.select(col("code"),lower(col("description")).alias("description"),col("NERSYN"), col("sty"),col("ner")).distinct().groupBy("code").agg(max("description").alias("description"), nerSyns, nerStype, nerSet).cache()

// COMMAND ----------

//display(groupedTuples)

// COMMAND ----------

//groupedTuples.selectExpr("code","description","TRANSFORM(NERSYN, ns->replace(description, ns[0], ns[1])) as alternatives","TRANSFORM(sty, styi->(TRANSFORM(ner, neri-> concat_ws(' ',neri,styi)))) as semantic").write.saveAsTable( "icd10.tempCorpus_3")

// COMMAND ----------

groupedTuples.selectExpr("code","description","TRANSFORM(NERSYN, ns->replace(description, ns[0], ns[1])) as alternatives","concat_ws(' ',ner,sty) as semantic").write.saveAsTable( "icd10.tempCorpus_3")

// COMMAND ----------

// MAGIC %sql select count(1) from (select code, description, explode(alternatives) alts from icd10.tempCorpus_3) 

// COMMAND ----------

// MAGIC %sql select code, description, explode(alternatives) alts from icd10.tempCorpus_3 order by code

// COMMAND ----------

// MAGIC %sql select code, description, count(alts) c from (select code, description, explode(alternatives) alts from icd10.tempCorpus_2) group by code, description order by c desc

// COMMAND ----------

// MAGIC %sql select distinct(sty)  from umls.mrsty

// COMMAND ----------

// MAGIC %sql select code, semantic from icd10.tempCorpus_3

// COMMAND ----------

val crp = spark.sql("select * from icd10.tempcorpus_3")

// COMMAND ----------

val finalCrp = crp.selectExpr("code","explode(alternatives) description").distinct().union(crp.select("code","description").distinct()).union(crp.selectExpr( "code", "replace(semantic,' ','_'").distinct())

// COMMAND ----------

finalCrp.orderBy("code").show(100,false)

// COMMAND ----------

val b = spark.read.csv("/andres/icd10/icd10_wsyn_fixed.csv").toDF(Seq("branch","branch_desc","code_","real","syn"): _*)

// COMMAND ----------

val augmentedFinalCorpus = finalCrp.union(b.selectExpr("replace(code_,'.','')","syn"))

// COMMAND ----------

augmentedFinalCorpus.write.saveAsTable("icd10.icd10cm_augmented")

// COMMAND ----------



// COMMAND ----------


