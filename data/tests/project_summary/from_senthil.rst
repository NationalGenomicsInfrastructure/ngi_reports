.. footer:: J.Lundberg_14_01_project_summary(###Page###/###Total###) 
.. header::
   .. image:: /proj/a2010002/nobackup/senthilp/delReport/images/ngi_scilife.gif 
      :align: center
      :width: 100%

.. |swedac| image:: /proj/a2010002/nobackup/senthilp/delReport/images/swedac_logo.gif
         :scale: 60%


.. |yes| image:: /proj/a2010002/nobackup/senthilp/delReport/images/yes.gif
         :scale: 45%

.. |no| image:: /proj/a2010002/nobackup/senthilp/delReport/images/no.gif
        :scale: 45%

Project overview
================

Project **J.Lundeberg_14_01(140117_Rapid_Ventana_TdT)** with 1 sample(s) is sequenced and all 
raw data with analysis data(if applicable) have been delivered to UPPMAX project ID **b2011007**.
Project was run on flowcell(s) 130517_SN7001301_0086_AD259NACXX. Please follow through the 
report for elobrated overview.

*Report name:* J.Lundberg_14_01_project_summary

*Date:* April 2, 2014

*Issued by:* SP

*Project duration:* 2014-01-23 to 2014-04-02

Project status
--------------

Sequencing finished.

User contact details
--------------------

jlundberg@ki.se

Order Information
-----------------
+-------------------------------+----------------------------------------+
|            **Field**          |                **Info**                |
+===============================+========================================+
|           Project name        |                J.Lundberg_14_01        |
+-------------------------------+----------------------------------------+
|           Project id          |                    P955                |
+-------------------------------+----------------------------------------+
|           Application         |               Finished library         |
+-------------------------------+----------------------------------------+
|            Run setup          |                   2x101                |
+-------------------------------+----------------------------------------+
|    Best practice analysis     |                     No                 |
+-------------------------------+----------------------------------------+
|          Lanes ordered        |                      2                 |
+-------------------------------+----------------------------------------+
|        Number of samples      |                      1                 |
+-------------------------------+----------------------------------------+
|        Reference Genome       |                    Other               |
+-------------------------------+----------------------------------------+
|     Minimum ordered reads(M)  |                   None                 |
+-------------------------------+----------------------------------------+
|        Order received         |                2014-01-10              |
+-------------------------------+----------------------------------------+
|       Contract received       |                2014-01-15              |
+-------------------------------+----------------------------------------+
|        Samples received       |                2014-01-20              |
+-------------------------------+----------------------------------------+
|            Queue date         |                2014-01-23              |
+-------------------------------+----------------------------------------+
|            UPPNEX id          |                b2011007                |
+-------------------------------+----------------------------------------+
|      UPPNEX project path      |  /proj/b2011007/INBOX/J.Lundberg_14_01 |
+-------------------------------+----------------------------------------+
|        All data delivered     |                2014-04-02              |
+-------------------------------+----------------------------------------+

Methods
-------

- *Library contructions:* 

  + **A:** Library was prepared using "650 bp insert standard DNA (Illumina TruSeq DNA)" protocol and clustering was done by cBot.

- *Sequencing:* 

  + **A:** All samples were sequenced on HiSeq2500 (HiSeq Control Software 2.0.12.0/RTA 1.17.21.3) with a 2x101 setup.The Bcl to Fastq conversion was performed using bcl2Fastq v1.8.3 from the CASAVA software suite. The quality scale used is Sanger / phred33 / Illumina 1.8+.

- *Data Flow:* All data (demultiplexed) from the instrument are collected and transfered securely to a storage server with well established pipeline.

- *Data Processing:* A set of standard quality checks were performed to assure that all sequenced data meet NGI guaranteed quality/quantity. All analysis are carried out in UPPMAX servers before delivering the raw data. 


+---------------------+-----------------------+
|  **Methods used**   | **Swedac accredited** |
+=====================+=======================+
| Library preparation |          |No|         |
+---------------------+-----------------------+
|    Sequencing data  |          |Yes|        |
+---------------------+-----------------------+
|       Data flow     |          |Yes|        |
+---------------------+-----------------------+
|    Data processing  |          |Yes|        |
+---------------------+-----------------------+

Sample Info
-----------

+----------------+--------------------------+------------------+--------------+
| **SciLife ID** |      **Submitted ID**    |     **Index**    | **Lib Prep** |
+================+==========================+==================+==============+
|    P955_101    | 140117_Rapid_Ventana_TdT | Index 8 (ACTTGA) |      A       |
+----------------+--------------------------+------------------+--------------+

Yield overview
--------------

+----------------+------------+-----------------+------------+----------------+------------+
|   **Sample**   | **Lib OC** | **Avg. FS(bp)** | **Q30(%)** | **MSequenced** | **Status** |
+================+============+=================+============+================+============+
|    P955_101    |   |yes|    |     350         |   59.34    |     105.66     |    |yes|   |
+----------------+------------+-----------------+------------+----------------+------------+

\* **Abrevations:** *Lib QC*: Recepetion control, *Avg. FS*: Average Fragment Size, *Q30*: Percentage of bases above quality score Q30 for the sample, *MSequenced*: Millions reads sequenced.

Run Info
---------

+------------+----------------+----------+-----------------+-------------+------------+------------------+-------------+
|  **Date**  |  **Pos-FCid**  | **Lane** | **Clusters(M)** | **PhiX(%)** | **Q30(%)** | **DRecovery(%)** | **SMethod** | 
+============+================+==========+=================+=============+============+==================+=============+
|   140123   |   B-H8A63ADXX  |     1    |      66.88      |     0.52    |    58.70   |       80.51      |      A      |
+------------+----------------+----------+-----------------+-------------+------------+------------------+-------------+
|   140123   |   B-H8A63ADXX  |     2    |      65.89      |     0.56    |    57.15   |       78.32      |      A      |
+------------+----------------+----------+-----------------+-------------+------------+------------------+-------------+

\* **Abrevations:** *Pos-FCid:* Position of flowcell-Flowcell ID,  *Q30(%):* Percentage of bases above quality score Q30 on the lane, *DRecovery*: Percentage of reads recovered after demultiplexing.

Information
-----------

**Naming conventions**

The data is delivered in fastq format using Illumina 1.8 quality
scores. There will be one file for the forward reads and one file for
the reverse reads (if the run was a paired-end run). 

The naming of the files follow the convention:

[LANE]_[DATE]_[POSITION][FLOWCELL]_[SCILIFE NAME]_[READ].fastq.gz

**Data access at UPPMAX**

Data from the sequencing will be uploaded to the UPPNEX (UPPMAX Next
Generation sequence Cluster Storage, www.uppmax.uu.se), from which the
user can access it. You can find the data in the INBOX folder of the UPPNEX project, which
was created for you when your order was placed, e.g. 

/proj/b2013000/INBOX/J.Doe_13_01

If you have problems to access your data, please
contact SciLifeLab genomics_support@scilifelab.se. If you have
questions regarding UPPNEX, please contact support@uppmax.uu.se.
     
**Acknowledgement**

In publications based on data from the work covered by this contract, the 
authors must acknowledge SciLifeLab, NGI and Uppmax: "The authors would 
like to acknowledge support from Science for Life Laboratory, the National 
Genomics Infrastructure, NGI, and Uppmax for providing assistance in massive 
parallel sequencing and computational infrastructure."


Regards
-------

Scilifelab Stockholm,

Tomtebodavägen 23A,

17165 Solna,

Sweden. 
