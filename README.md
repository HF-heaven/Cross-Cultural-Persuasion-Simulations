# Cross-Cultural Persuasion Simulations

This repository contains the code for the EMNLP 2025 paper: **Enhancing LLM-Based Persuasion Simulations with Cultural and Speaker-Specific Information**.

This repository contains the implementation of cross-cultural persuasion dialogue generation framework, supporting multiple experimental modes corresponding to different research frameworks described in the paper.

## Framework Modes

The code supports 5 different modes that correspond to different experimental frameworks:

### Mode 1: PersuaSim-Orig (Baseline)
- **Description**: Basic persuasion dialogue without cultural profiles
- **Features**: Standard two-agent persuasion without cultural context
- **Language**: English only
- **Use Case**: Baseline comparison for cultural effects

### Mode 2: PersuaSim-Infused (Cultural Profiles)
- **Description**: Persuasion with cultural background injection
- **Features**: Agents maintain assigned cultural profiles throughout conversation
- **Language**: English only
- **Use Case**: Testing cultural influence on persuasion dynamics

### Mode 3: PersuaSim-Reinforced-MultiLing (Enhanced Cultural + Multilingual)
- **Description**: Enhanced cultural alignment with multilingual support
- **Features**: 
  - Stronger cultural background alignment
  - Agents speak in their native languages
  - Language verification filter (3.2)
- **Use Case**: Cross-cultural communication with enhanced cultural expression
- **Note**: PersuaSim-Reinforced (English-only version) and PersuaSim-Infused-MultiLing can be easily implemented through simple code modifications

### Mode 4: Free-Stance-Multilingual (Free Stance + Multilingual)
- **Description**: Free stance expression with multilingual generation
- **Features**:
  - Cultural background injection
  - Multilingual generation
  - No explicit stance provision (free stance analysis)
  - Language verification filter (3.2)
- **Use Case**: Natural cultural expression without explicit positioning in native languages

### Mode 5: Free-Stance-English (Free Stance + English)
- **Description**: Free stance expression in English
- **Features**:
  - Cultural background injection
  - English only
  - No explicit stance provision (free stance analysis)
- **Use Case**: Natural cultural expression without explicit positioning in English

## Configuration Parameters

### Required Parameters

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `mode` | Framework mode (1-5) | `1`, `2`, `3`, `4`, `5` |
| `api_key` | OpenAI API key | `'your_api_key'` |
| `LLM` | Language model | `'gpt-3.5-turbo'`, `'gpt-4'`, `'gpt-4o'` |
| `input_file` | Topics and stances CSV file | `'test_topics_stances.csv'` |

### Mode-Specific Behavior

- **Mode 1**: No cultural profiles, English only
- **Mode 2**: Cultural profiles, English only (PersuaSim-Infused)
- **Mode 3**: Enhanced cultural profiles, multilingual generation (PersuaSim-Reinforced-MultiLing)
- **Mode 4**: Cultural profiles, multilingual generation, free stance (Free-Stance-Multilingual)
- **Mode 5**: Cultural profiles, English only, free stance (Free-Stance-English)

## Data Files

### 1. `culture_profiles.json`
Contains detailed cultural profiles for different ethnic/cultural groups:

```json
{
    "Arabic": [
        "You are Ali Al-Salem, an Arab male. Born in Riyadh, Saudi Arabia...",
        "You are Samira El-Masri, an Arab female. You were born and raised in Cairo, Egypt..."
    ],
    "Bengali": [
        "You are Pritam Chatterjee, a Bengali male born in Kolkata, West Bengal...",
        "You are Mousumi Sen, a female Bengali, born and raised in Dhaka, Bangladesh..."
    ]
}
```

**Structure**:
- **Keys**: Cultural/ethnic group names (e.g., "Arabic", "Bengali", "Chinese")
- **Values**: Arrays of detailed character profiles including:
  - Name, gender, age
  - Birthplace and nationality
  - Education and profession
  - Personal interests and hobbies
  - Significant life events or achievements

### 2. `test_topics_stances.csv`
Contains debate topics and cultural stance data:

**Columns**:
- `question`: Question ID (e.g., "Q34", "Q122")
- `pair`: Country pair code (e.g., "BGD_DEU", "JPN_TUR")
- `distance`: Cultural distance between countries
- `country1`, `country2`: Country codes for the two participants
- `Binary score_country1`, `Binary score_country2`: Binary stance scores
- `Weighted score country1`, `Weighted score country2`: Weighted stance scores
- `q_content`: Full question text
- `topic`: Topic category (e.g., "SOCIAL VALUES", "MIGRATION", "SCIENCE & TECHNOLOGY")
- `view1`, `view2`: Stance labels ("Agree", "Disagree")

**Example**:
```csv
question,pair,distance,country1,country2,Binary score_country1,Binary score_country2,Weighted score country1,Weighted score country2,q_content,topic,view1,view2
Q34,BGD_DEU,0.484046563,BGD,DEU,0.774030354,-0.220822281,1.295109612,-0.466843501,"When jobs are scarce, employers should give priority to people of this country over immigrants",SOCIAL VALUES,Agree,Disagree
```

## Output Structure

Generated conversations are saved as JSON files with the following structure:

```json
{
    "Initial Setting": {
        "Persuader": "Initial persuader prompt with cultural profile...",
        "Persuadee": "Initial persuadee prompt with cultural profile...",
        "Judge": "Initial judge prompt..."
    },
    "Conversation History": {
        "0": {
            "Persuader": "First persuader message...",
            "Persuadee": "First persuadee response..."
        },
        "1": {
            "Persuader": "Second persuader message...",
            "Persuadee": "Second persuadee response..."
        }
    },
    "Result": {
        "is_agreement": "Yes/No",
        "winner": "0/1/Neither"
    }
}
```

## File Organization

Output files are organized as:
```
version4/Result_withCultureProfiles/
├── 1/  # Mode 1 results
├── 2/  # Mode 2 results  
├── 3/  # Mode 3 results
├── 4/  # Mode 4 results
└── 5/  # Mode 5 results
    └── {topic_id}-{country1}-{culture1}-{culture2}-{run_id}.json
```

## Usage Example

```python
# Set your parameters
mode = 3  # Choose framework mode (1-5)
api_key = 'your_openai_api_key'
LLM = 'gpt-4o'
input_file = 'test_topics_stances.csv'

# Run the experiment
python generate_conversation_cultureRolePlay_Modified.py
```

## Quality Monitoring

The framework includes several quality monitoring agents:

1. **Utterance Quality Monitor (3.0)**: Agent identity and role maintenance
2. **Cultural Background Conflict Detection (3.1)**: Detects cultural misalignment
3. **Language Verification Filter (3.2)**: Ensures correct language usage (modes 3,4)

## Documentation

For detailed technical documentation, please refer to the following PDF files:

### 📋 [original_structure.pdf](original_structure.pdf)
- **Purpose**: Provides the original framework structure and design principles
- **Content**: Detailed explanation of the base PersuaSim framework architecture
- **Use Case**: Understanding the foundational design before cultural enhancements

### 🔍 [monitor_detail.pdf](monitor_detail.pdf)
- **Purpose**: Comprehensive guide to the quality monitoring system
- **Content**: Detailed specifications of all monitoring agents (3.0, 3.1, 3.2) and their implementation
- **Use Case**: Understanding how the framework ensures conversation quality and cultural alignment

These documents provide in-depth technical details that complement the code implementation and help users understand the theoretical foundations and quality assurance mechanisms of the framework.

## Citation

If you use this code in your research, please cite the corresponding paper:

```bibtex
@inproceedings{ma2025communication,
  title={Communication Makes Perfect: Persuasion Dataset Construction via Multi-LLM Communication},
  author={Ma, Weicheng and Zhang, Hefan and Yang, Ivory and Ji, Shiyu and Chen, Joice and Hashemi, Farnoosh and Mohole, Shubham and Gearey, Ethan and Macy, Michael and Hassanpour, Saeed and others},
  booktitle={Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)},
  pages={4017--4045},
  year={2025}
}
```

## Framework Extensions

The current implementation provides a solid foundation that can be easily extended to support additional framework variants:

### PersuaSim-Reinforced (English-only)
To implement PersuaSim-Reinforced with English-only generation:
- Modify the language settings in Mode 3 to force English output
- Remove multilingual translation components
- Keep the enhanced cultural alignment features

### PersuaSim-Infused-MultiLing
To implement PersuaSim-Infused-MultiLing:
- Combine Mode 2's cultural profile injection with Mode 3's multilingual capabilities
- Use basic cultural profiles (not enhanced) with native language generation
- Apply language verification filters

These extensions can be achieved through simple parameter modifications and conditional logic adjustments in the existing codebase.

## Requirements

- Python 3.7+
- OpenAI API access
- Required packages: `requests`, `pandas`, `json`, `time`, `os`