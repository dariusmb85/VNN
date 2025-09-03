# VNN
Experiments with VisualNeuralNetworks

## Running the scripts
First thing you want to do is access your source for your data. In the case of my black box it is, https://boonelab.ccbr.utoronto.ca/supplement/costanzo2009/. You want to go there to download the largest file "sgadata_costanzo2009_rawdata_101120.txt.gz". From here we will go into our preprocessing of the data with: 
#### SGA_raw_data_ingest.R

This will provide you with the proper input files for the black box. Also note during this process you need the location of the filtered allele_list. It's called 20231219_final_gene_list.txt in this procedure. 

# Visual Neural Networks (VNN) for Yeast Growth Prediction

This repository explores how **neural network models** can be used to predict yeast growth outcomes when specific genes are knocked out.  
We combine **Synthetic Genetic Array (SGA)** experimental data with **deep learning models** to study how gene–gene interactions shape growth phenotypes.  

📂 Repository: [dariusmb85/VNN (main branch)](https://github.com/dariusmb85/VNN/tree/main)

---

## 📌 Project Motivation

- **Biology**: Yeast (*Saccharomyces cerevisiae*) is a model organism for studying genetics. By systematically deleting genes, researchers can measure how individual and paired knockouts affect cell growth.  
- **Computation**: This repo builds **neural networks** to learn the mapping between **knockout profiles** and **growth measurements**.  
- **Goal**: Compare **black-box neural networks** (standard ANNs, CNNs) to more interpretable **Visible Neural Networks (VNNs)** that reflect biological structure.

---

## 📂 Repository Structure

├── dcell_blackBox_NeuralNet.py # Train black-box ANN on yeast knockout-growth data
├── PostAnalysisCNN.py # Analyze and visualize CNN experiment results
├── utils.py # Utility functions (data handling, preprocessing)
├── SGA_raw_data_injest.R # Ingest raw Synthetic Genetic Array (SGA) datasets
├── Subset_Growth_File.R # Preprocess & subset yeast growth data
├── README.md # Project documentation
└── .gitignore # Git ignore configuration

