# Data_Validator
This is a python scipt that was made to easily standardize the inputs for my nextflow pipelines, as well as do some basic checks to ensure input files are in the format I expect. There are three basic features inculded with the scipt, outlined below. Checked and formatted data will always be output to Validated_Data in the same directory as data_validator.py (/work in the docker container).

# Obtaining Data_Validator
data_validator.py can be used with base python 3.11.5, and has not be tested with any other version. (Although it probably works fine.)

data_validator can also be obtained via the prebuild docker container, as below:
```sh
docker pull ebird013/data_validator:1.0
```

# Data_validator in FastQ Paired-End mode
In this mode data_validator can take single line Paired FastQ files (Gzipped or uncompressed). It looks for the hallmarks of a proper fastq file, and then outputs paired files (gzipped or not) nammed according to input sample name. Currently there is no support for multiline fastqs, or concatenating sequencing runs.

Running with Docker: (While in the directory with your FastQs):

Retun uncompressed fastqs:
```sh
docker run -v .:/work PE_FQ /work/{R1_Fastq_file_name} /work/{R2_Fastq_file_name}  {sample name}
```
Retun compressed fastqs:
```sh
docker run -v .:/work PE_FQ /work/{R1_Fastq_file_name} /work/{R2_Fastq_file_name}  {sample name} --gzip
```

Running locally:

Retun uncompressed fastqs:
```sh
data_validator.py PE_FQ {R1_Fastq_file_name} {R2_Fastq_file_name}  {sample name}
```
Retun compressed fastqs:
```sh
data_validator.py PE_FQ {R1_Fastq_file_name} {R2_Fastq_file_name}  {sample name} --gzip
```

# Data_validator in FastQ Single-End Mode
This mode is the same as PE mode, with one additional funciton. In addition to the checks prformed in PE mode, SE mode can also rename sequences in fastqs (--rename). This has been particularly useful with some long read dataseqs that have overly complex sequence names.

Running with Docker: (While in the directory with your FastQs):
```sh
docker run -v .:/work SE_FQ /work/{Fastq_file_name}  {sample name} {Optional: --gzip, --rename}
```

Running locally:
```sh
data_validator.py SE_FQ {R1_Fastq_file_name} {R2_Fastq_file_name}  {sample name} {Optional: --gzip, --rename}
```

#Data_Validator in Fasta Mode
In this mode datavalidator can take single line OR multi-line Fasta formatted files (Gzipped or uncompressed). It works with DNA/RNA/protein fastas. I can also output compressed or uncompressed fasta files. It will always output single line fastas.

Running with Docker: (While in the directory with your FastQs):
```sh
docker run -v .:/work FA /work/{Fasta_file_name} {Optional: --gzip}
```

Running locally:
```sh
data_validator.py FA {Fasta_file_name} {Optional: --gzip}
```
