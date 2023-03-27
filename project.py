# -*- coding: utf-8 -*-
import pandas as pd
import janitor
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import random

def clean_exercise_name(exercise_name):
    # Remove extra spaces before or after parentheses
    cleaned_name = re.sub(r'\s*\(\s*', ' (', exercise_name)
    cleaned_name = re.sub(r'\s*\)\s*', ')', cleaned_name)
    # Replace "Hammer Curl (Dumbbell)" with "Hammer Curl"
    cleaned_name = cleaned_name.replace("Hammer Curl (Dumbbell)", "Hammer Curl")

    return cleaned_name

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

    # Define a lambda function to check if 'tricep' is in the exercise name
    check_for_tricep = lambda x: 'Triceps' if 'tricep' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'bicep' is in the exercise name
    check_for_bicep = lambda x: 'Biceps' if 'bicep' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'dips' is in the exercise name
    check_for_dips = lambda x: 'Chest' if 'dips' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'bench' is in the exercise name
    check_for_bench = lambda x: 'Chest' if 'bench' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'incline press' is in the exercise name
    check_for_incline = lambda x: 'Chest' if 'incline press' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'cable fly' is in the exercise name
    check_for_fly = lambda x: 'Chest' if 'cable fly' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'hammer curl' is in the exercise name
    check_for_hammer = lambda x: 'Biceps' if 'hammer curl' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'military press' is in the exercise name
    check_for_military = lambda x: 'Shoulders' if 'military press' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'lateral raise' is in the exercise name
    check_for_lateral = lambda x: 'Shoulders' if 'lateral raise' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'shoulder' is in the exercise name
    check_for_shoulder = lambda x: 'Shoulders' if 'shoulder' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'skullcrusher' is in the exercise name
    check_for_skullcrusher = lambda x: 'Triceps' if 'skullcrusher' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'overhead press' is in the exercise name
    check_for_overhead = lambda x: 'Shoulders' if 'overhead press' in x['exercise_name'].lower() else x['muscle_group']

    # Define a lambda function to check if 'rotator cuff work' is in the exercise name
    check_for_rotator = lambda x: 'Shoulders' if 'rotator cuff work' in x['exercise_name'].lower() else x[
        'muscle_group']

    # Apply the lambda functions to the muscle_group column
    dataset = dataset.copy()
    dataset['muscle_group'] = dataset.apply(check_for_tricep, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_bicep, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_dips, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_bench, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_incline, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_fly, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_hammer, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_military, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_lateral, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_shoulder, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_skullcrusher, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_overhead, axis=1)
    dataset['muscle_group'] = dataset.apply(check_for_rotator, axis=1)

    return dataset

def clean_workout_name(workout_name):
    # Replace "shoulder" with "shoulders"
    cleaned_name = workout_name.replace('shoulder', 'shoulders')

    # Replace "squat" with "legs"
    cleaned_name = cleaned_name.replace('squat', 'legs')

    # Remove digits and punctuation marks
    cleaned_name = re.sub(r'[\d\W_]+', ' ', cleaned_name)

    # Convert to lowercase and strip leading/trailing spaces
    return cleaned_name.lower().strip()

def extract_muscle_group(workout_name):
    # Define a list of known muscle group names
    muscle_groups = ['chest', 'legs', 'back', 'shoulders']

    # Use a regular expression pattern to match muscle group names
    pattern = r'\b(' + '|'.join(muscle_groups) + r')\b'
    match = re.search(pattern, workout_name, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        return None

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


def run_model(apiArgs):
    dataset = preprocess_dataset()
    return generate_recommendations(dataset, apiArgs)