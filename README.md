# PDF Processing Docker Application

This Docker application processes PDF files to extract titles and outlines using machine learning models. The application uses pre-trained models to classify headings (H1, H2, H3) and generates structured JSON output.

## Features

- **PDF Text Extraction**: Uses `pdfplumber` to extract text and metadata from PDF documents
- **ML-Powered Heading Classification**: Pre-trained models classify headings into H1, H2, and H3 levels
- **Smart Title Detection**: Automatically identifies document titles based on font size, boldness, and position
- **Structured Output**: Generates JSON output with document title and hierarchical outline
- **Batch Processing**: Processes multiple PDF files in a single run
- **Docker Containerization**: Fully containerized for easy deployment and consistency

## Project Structure

```
Challenge_1a/
├── process_pdfs.py              # Main PDF processing script
├── models/                      # Pre-trained machine learning models
│   ├── headings_model.pkl      # Trained model for heading classification
│   └── label_encoder.pkl       # Label encoder for model predictions
├── dataset/
│   └── schema/
│       └── output_schema.json  # JSON schema for output format
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .dockerignore               # Docker build exclusions
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Docker installed on your system
- PDF files to process

### 1. Build the Docker Image

```bash
docker build -t pdf-processor .
```

### 2. Prepare Your PDFs

Create an input directory and add your PDF files:

```bash
mkdir -p input
# Copy your PDF files to the input directory
cp your-pdfs/*.pdf input/
```

### 3. Run the Container

```bash
# Create output directory
mkdir -p output

# Run the container with volume mounts
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-processor
```

### 4. Alternative: Interactive Mode

```bash
# Run container in interactive mode for debugging
docker run -it -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-processor /bin/bash
```

## Input/Output

### Input
- **Format**: PDF files (`.pdf`)
- **Location**: Mount to `/app/input/` directory
- **Processing**: All PDF files in the input directory will be processed

### Output
- **Format**: JSON files (`.json`)
- **Location**: Generated in `/app/output/` directory
- **Naming**: Each PDF gets a corresponding JSON file with the same name

### Output Schema

The application generates JSON output following this structure:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Main Heading",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Sub Heading",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Sub-sub Heading", 
      "page": 2
    }
  ]
}
```

## Technical Details

### Dependencies

- **Python 3.10**: Base runtime environment
- **pdfplumber 0.11.7**: PDF text extraction and analysis
- **pandas 2.2.3**: Data manipulation and processing
- **scikit-learn 1.7.1**: Machine learning framework
- **joblib 1.5.1**: Model serialization and loading
- **numpy 2.2.5**: Numerical computations

### ML Model Features

The heading classification model uses the following features:
- **Font Size**: Average font size of text elements
- **Position**: X and Y coordinates on the page
- **Text Length**: Number of characters in the text
- **Uppercase Ratio**: Proportion of uppercase characters
- **Bold Detection**: Whether text is in bold font
- **Numbering**: Whether text starts with numbers

### Processing Pipeline

1. **PDF Parsing**: Extract text and metadata using pdfplumber
2. **Feature Extraction**: Calculate ML features for each text line
3. **Heading Classification**: Use pre-trained model to classify headings
4. **Title Detection**: Identify document title from first page
5. **Outline Generation**: Create hierarchical structure from headings
6. **JSON Output**: Save results in structured format

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure input/output directories have proper read/write permissions
2. **Model Loading Errors**: Verify model files are present in `models/` directory
3. **Memory Issues**: For large PDFs, consider increasing Docker memory limits
4. **Empty Output**: Check if PDFs contain extractable text (not scanned images)

### Debug Mode

Run the container interactively to debug issues:

```bash
docker run -it -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-processor /bin/bash
```

Then manually run the script:
```bash
python process_pdfs.py
```

## Development

### Modifying the Application

1. Edit `process_pdfs.py` with your changes
2. Rebuild the Docker image: `docker build -t pdf-processor .`
3. Test with your PDF files

### Adding New Features

- **New ML Features**: Add feature extraction in the processing loop
- **Output Formats**: Modify the JSON generation section
- **Model Updates**: Replace model files in `models/` directory

## Performance

- **Processing Speed**: ~1-2 seconds per page depending on content complexity
- **Memory Usage**: ~100-200MB per PDF file
- **Accuracy**: Optimized for academic and technical documents

## License

This project is for educational and research purposes. The pre-trained models are included for demonstration.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your PDF files are text-based (not scanned images)
3. Ensure all dependencies are properly installed 