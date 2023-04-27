# -*- coding: utf-8 -*-
import pandas as pd
import janitor
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import random

# This function cleans exercise names by replacing specific substrings with other substrings
def clean_exercise_name(exercise_name):
    # Remove extra spaces before or after parentheses
    cleaned_name = re.sub(r'\s*\(\s*', ' (', exercise_name)
    cleaned_name = re.sub(r'\s*\)\s*', ')', cleaned_name)
    # Replace "Hammer Curl (Dumbbell)" with "Hammer Curl"
    cleaned_name = cleaned_name.replace("Hammer Curl (Dumbbell)", "Hammer Curl")
    # Replace "Lat Pulldown " with "Lat Pulldown"
    cleaned_name = cleaned_name.replace("Lat Pulldown ", "Lat Pulldown")
    # Replace "Lateral Raise (Dumbbells)" with "Lateral Raise (Dumbbell)"
    cleaned_name = cleaned_name.replace("Lateral Raise (Dumbbells)", "Lateral Raise (Dumbbell)")
    # Replace "Lat Pulldown (Cable)" with "Lat Pulldown"
    cleaned_name = cleaned_name.replace("Lat Pulldown(Cable)", "Lat Pulldown")
    # Replace "Seated Military Press" with "Seated Shoulder  Press (Barbell)"
    cleaned_name = cleaned_name.replace("Seated Military Press", "Seated Shoulder  Press (Barbell)")
    # Replace ""Seated Shoulder  Press (Barbell) (Dumbbell)"" with "Seated Shoulder Press (Dumbbell)"
    cleaned_name = cleaned_name.replace("Seated Shoulder  Press (Barbell) (Dumbbell)", "Seated Shoulder Press (Dumbbell)")
    # Replace "Military Press (Standing)" with "Shoulder Press (Standing)"
    cleaned_name = cleaned_name.replace("Military Press (Standing)", "Shoulder Press (Standing)")
    # Replace "Incline Bench Press (Barbell)" with "Incline Bench Press"
    cleaned_name = cleaned_name.replace("Incline Bench Press (Barbell)", "Incline Bench Press")
    # Replace "Curl Dumbbell" with "Bicep Curl (Dumbbell)"
    cleaned_name = cleaned_name.replace("Curl Dumbbell", "Bicep Curl (Dumbbell)")

    return cleaned_name

# This function updates the muscle group names in the dataset based on keywords in exercise names
def clean_muscle_group_names(dataset):
    keywords_to_muscle_group = {
        'tricep': 'Triceps',
        'bicep': 'Biceps',
        'dips': 'Chest',
        'bench': 'Chest',
        'incline press': 'Chest',
        'cable fly': 'Chest',
        'hammer curl': 'Biceps',
        'curl ez': 'Biceps',
        'curl dumbbell': 'Biceps',
        'military press': 'Shoulders',
        'lateral raise': 'Shoulders',
        'shoulder': 'Shoulders',
        'skullcrusher': 'Triceps',
        'stairmaster': 'Legs',
        'overhead press': 'Shoulders',
        'rotator cuff work': 'Shoulders',
        'chin up': 'Back'
    }

    def update_muscle_group(row):
        for keyword, muscle_group in keywords_to_muscle_group.items():
            if keyword in row['exercise_name'].lower():
                return muscle_group
        return row['muscle_group']

    dataset = dataset.copy()
    dataset['muscle_group'] = dataset.apply(update_muscle_group, axis=1)
    return dataset

# This function preprocesses the dataset by cleaning variable names, dropping unnecessary columns,
# converting weight values to kg, and extracting muscle group names from workout names
def preprocess_dataset():
    dataset = pd.read_csv('Dataset/weightlifting_721_workouts.csv')

    # Clean variable names and select first 6 columns
    dataset = (
        dataset
        .clean_names()
        .iloc[:, :6]
    )

    # Title-case exercise_name and workout_name columns, and convert 2nd to 4th columns to factors
    dataset[['exercise_name', 'workout_name']] = (
        dataset[['exercise_name', 'workout_name']]
        .apply(lambda x: x.str.replace('.', '', regex=True).str.title())
    )

    dataset['exercise_name'] = dataset['exercise_name'].apply(clean_exercise_name)

    dataset[dataset.columns[1:4]] = dataset.iloc[:, 1:4].astype('category')

    # Convert weight column from lbs to kg
    dataset['weight'] = dataset['weight'].apply(lambda x: x * 0.453592)

    # Round the 'weight' column down to the nearest integer
    dataset['weight'] = dataset['weight'].apply(lambda x: int(x))

    # Create a new DataFrame containing the counts of each unique value in the 'exercise_name' column
    exercise_counts = pd.DataFrame(dataset['exercise_name'].value_counts())

    # Remove the column named 'column_to_remove'
    dataset = dataset.drop(columns=['date'])
    dataset = dataset.drop(columns=['set_order'])

    # Save the updated dataset
    dataset.to_csv('dataset.csv', index=False)

    # Define a regular expression pattern to extract muscle group name from workout_name
    pattern = r'([A-Za-z]+)'

    # Apply the extract_muscle_group function to workout_name column
    dataset['muscle_group'] = dataset['workout_name'].apply(extract_muscle_group)

    # Drop rows where the muscle_group column is None
    dataset = dataset.dropna(subset=['muscle_group'])

    # Clean muscle group names
    dataset = clean_muscle_group_names(dataset)

    return dataset

# This function cleans workout names by standardizing the spelling of certain words and removing digits and punctuation marks
def clean_workout_name(workout_name):
    # Replace "shoulder" with "shoulders"
    cleaned_name = workout_name.replace('shoulder', 'shoulders')

    # Replace "squat" with "legs"
    cleaned_name = cleaned_name.replace('squat', 'legs')

    # Remove digits and punctuation marks
    cleaned_name = re.sub(r'[\d\W_]+', ' ', cleaned_name)

    # Convert to lowercase and strip leading/trailing spaces
    return cleaned_name.lower().strip()

# This function extracts muscle group names from workout names using regular expressions
def extract_muscle_group(workout_name):
    # Define a list of known muscle group names
    muscle_groups = ['chest', 'legs', 'back', 'shoulders']

    # Use a regular expression pattern to match muscle group names
    pattern = fr'\b({"|".join(muscle_groups)})\b'
    match = re.search(pattern, workout_name, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None

# This function generates personalized exercise recommendations based on user preferences and dataset features
def generate_recommendations(dataset, apiArgs):
    preferences = {}
    muscleArr = []
    for muscleNum in range(len(apiArgs.muscleGroups)):
        preferences[apiArgs.muscleGroups[muscleNum].muscleType] = {'reps': apiArgs.muscleGroups[muscleNum].reps,
                           'weight': apiArgs.muscleGroups[muscleNum].weight}
        muscleArr.append(apiArgs.muscleGroups[muscleNum].muscleType)


    # Filter the dataset to only include exercises for the user's chosen muscle groups
    dataset = dataset[dataset['muscle_group'].isin(muscleArr)]

    # Extract the relevant columns from the dataset
    exercise_features = dataset[['muscle_group', 'reps', 'weight', 'exercise_name']]

    # Compute similarity scores between the user preferences and the exercise features
    exercise_vectors = []
    for i in range(len(exercise_features)):
        exercise = exercise_features.iloc[i]
        exercise_vector = []
        for muscle in muscleArr:
            if exercise['muscle_group'] == muscle:
                exercise_vector.extend([preferences[muscle]['weight'], preferences[muscle]['reps']])
            else:
                exercise_vector.extend([0, 0])
        exercise_vectors.append(exercise_vector)

    user_vector = []
    for muscle in muscleArr:
        user_vector.extend([preferences[muscle]['weight'], preferences[muscle]['reps']])

    similarity_scores = cosine_similarity([user_vector], exercise_vectors)[0]

    # Rank the exercises for each muscle group based on their similarity scores and recommend the top 5
    num_recommendations = 20
    top_exercises_by_muscle = {}
    for muscle in muscleArr:
        muscle_df = exercise_features[exercise_features['muscle_group'] == muscle]
        muscle_df = muscle_df.assign(similarity_score=np.abs(muscle_df['reps'] - preferences[muscle]['reps']) + np.abs(
            muscle_df['weight'] - preferences[muscle]['weight']))
        muscle_df = muscle_df.assign(combined_score=muscle_df['similarity_score'] + (1 / muscle_df['similarity_score']))
        muscle_df = muscle_df.sort_values('combined_score')
        top_exercises_by_muscle[muscle] = muscle_df[:num_recommendations][
            ['exercise_name', 'reps', 'weight', 'muscle_group']].values.tolist()

    # Randomly select up to 5 unique exercises from the top 20 recommended exercises for each muscle group
    random_recommendations = []
    for muscle, exercises in top_exercises_by_muscle.items():
        unique_exercises = []
        random.shuffle(exercises)  # Randomize the order of exercises

        for exercise in exercises:
            if exercise[0] not in [ex[0] for ex in unique_exercises]:  # Check if the exercise name is unique
                unique_exercises.append(exercise)
                if len(unique_exercises) == 5:  # Stop adding exercises once 5 unique ones have been selected
                    break

        random_recommendations.extend(unique_exercises)
    return random_recommendations

# This function preprocesses the dataset and generates exercise recommendations based on user preferences
def run_model(apiArgs):
    dataset = preprocess_dataset()
    return generate_recommendations(dataset, apiArgs)