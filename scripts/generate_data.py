import os
import random
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_FILE = os.path.join(DATA_DIR, "pet_diseases.csv")

DISEASES = {
    "dog": [
        "Parvovirus", "Canine Distemper", "Kennel Cough", "Canine Hip Dysplasia", 
        "Canine Heartworm", "Canine Leptospirosis", "Canine Bloat (GDV)", 
        "Canine Arthritis", "Canine Mange", "Canine Ear Infection", "Canine UTI", 
        "Canine Obesity", "Canine Diabetes", "Canine Allergies", "Rabies (Dog)"
    ],
    "cat": [
        "Feline Upper Respiratory Infection", "Feline Panleukopenia", 
        "Feline Leukemia (FeLV)", "Feline Immunodeficiency Virus (FIV)", 
        "Feline Diabetes", "Feline Hyperthyroidism", "Feline Kidney Disease", 
        "Feline Lower Urinary Tract Disease (FLUTD)", "Feline Ringworm", 
        "Feline Ear Mites", "Feline Asthma", "Feline Inflammatory Bowel Disease", 
        "Feline Obesity", "Rabies (Cat)", "Feline Heartworm"
    ]
}

SYMPTOMS_BY_DISEASE = {
    "Parvovirus": ["vomiting", "diarrhea", "lethargy", "loss_of_appetite", "fever"],
    "Canine Distemper": ["fever", "coughing", "sneezing", "lethargy", "vomiting", "diarrhea", "seizures"],
    "Kennel Cough": ["coughing", "sneezing", "lethargy", "loss_of_appetite"],
    "Canine Hip Dysplasia": ["limping", "stiffness", "pain", "reluctance_to_exercise"],
    "Canine Heartworm": ["coughing", "lethargy", "loss_of_appetite", "weight_loss", "breathing_difficulty"],
    "Canine Leptospirosis": ["fever", "vomiting", "lethargy", "loss_of_appetite", "increased_thirst", "frequent_urination"],
    "Canine Bloat (GDV)": ["swollen_abdomen", "restlessness", "drooling", "retching", "pain"],
    "Canine Arthritis": ["stiffness", "limping", "pain", "reluctance_to_exercise", "lethargy"],
    "Canine Mange": ["itching", "hair_loss", "redness", "scabs"],
    "Canine Ear Infection": ["head_shaking", "scratching_ears", "odor_from_ears", "redness", "discharge_from_ears"],
    "Canine UTI": ["frequent_urination", "straining_to_urinate", "blood_in_urine", "accidents_in_house"],
    "Canine Obesity": ["weight_gain", "lethargy", "breathing_difficulty", "reluctance_to_exercise"],
    "Canine Diabetes": ["increased_thirst", "frequent_urination", "weight_loss", "increased_appetite", "lethargy"],
    "Canine Allergies": ["itching", "hair_loss", "redness", "sneezing", "runny_eyes"],
    "Rabies (Dog)": ["aggression", "restlessness", "drooling", "seizures", "paralysis", "fever"],

    "Feline Upper Respiratory Infection": ["sneezing", "runny_nose", "runny_eyes", "fever", "loss_of_appetite", "lethargy"],
    "Feline Panleukopenia": ["vomiting", "diarrhea", "lethargy", "loss_of_appetite", "fever", "weight_loss"],
    "Feline Leukemia (FeLV)": ["lethargy", "weight_loss", "fever", "swollen_lymph_nodes", "pale_gums"],
    "Feline Immunodeficiency Virus (FIV)": ["lethargy", "weight_loss", "fever", "swollen_lymph_nodes", "diarrhea"],
    "Feline Diabetes": ["increased_thirst", "frequent_urination", "weight_loss", "increased_appetite", "lethargy"],
    "Feline Hyperthyroidism": ["weight_loss", "increased_appetite", "increased_thirst", "frequent_urination", "restlessness", "vomiting"],
    "Feline Kidney Disease": ["increased_thirst", "frequent_urination", "weight_loss", "lethargy", "vomiting", "loss_of_appetite"],
    "Feline Lower Urinary Tract Disease (FLUTD)": ["frequent_urination", "straining_to_urinate", "blood_in_urine", "crying_while_urinating", "accidents_outside_litter_box"],
    "Feline Ringworm": ["hair_loss", "redness", "scabs", "itching"],
    "Feline Ear Mites": ["head_shaking", "scratching_ears", "odor_from_ears", "discharge_from_ears"],
    "Feline Asthma": ["coughing", "breathing_difficulty", "wheezing", "lethargy"],
    "Feline Inflammatory Bowel Disease": ["vomiting", "diarrhea", "weight_loss", "loss_of_appetite", "lethargy"],
    "Feline Obesity": ["weight_gain", "lethargy", "breathing_difficulty", "reluctance_to_exercise"],
    "Rabies (Cat)": ["aggression", "restlessness", "drooling", "seizures", "paralysis", "fever"],
    "Feline Heartworm": ["coughing", "breathing_difficulty", "vomiting", "lethargy", "weight_loss"]
}

ALL_SYMPTOMS = sorted(list(set([sym for symptoms in SYMPTOMS_BY_DISEASE.values() for sym in symptoms])))

def generate_data(num_samples=5000):
    data = []
    for _ in range(num_samples):
        pet_type = random.choice(["dog", "cat"])
        disease = random.choice(DISEASES[pet_type])
        
        # Base symptoms
        base_symptoms = SYMPTOMS_BY_DISEASE[disease]
        
        # Add a bit of noise (drop some, add some random)
        actual_symptoms = set()
        for sym in base_symptoms:
            if random.random() > 0.1: # 90% chance to keep a core symptom
                actual_symptoms.add(sym)
                
        # Add random noise symptom
        if random.random() > 0.7:
             actual_symptoms.add(random.choice(ALL_SYMPTOMS))

        # Ensure at least one symptom exists
        if not actual_symptoms:
             actual_symptoms.add(random.choice(base_symptoms))

        row = {"pet_type": pet_type, "disease": disease}
        for sym in ALL_SYMPTOMS:
            row[sym] = 1 if sym in actual_symptoms else 0
            
        data.append(row)
        
    df = pd.DataFrame(data)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(DATA_FILE, index=False)
    print(f"Generated {len(df)} records in {DATA_FILE}")

if __name__ == "__main__":
    generate_data()
