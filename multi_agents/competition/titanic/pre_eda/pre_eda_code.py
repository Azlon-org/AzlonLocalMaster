def generated_code_function():
    
    import pandas as pd
    
    # Load the datasets
    train_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/train.csv'
    test_path = '/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/test.csv'
    
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    # Display the first few rows of each dataset
    print("First few rows of the training dataset:")
    print(train_df.head())
    
    print("\nFirst few rows of the test dataset:")
    print(test_df.head())
    
    # Check the dimensions of the datasets
    print("\nDimensions of the training dataset:", train_df.shape)
    print("Dimensions of the test dataset:", test_df.shape)
    
    
    # Understand the data types and basic statistics
    print("\nInformation about the training dataset:")
    print(train_df.info())
    
    print("\nSummary statistics of the training dataset:")
    print(train_df.describe())
    
    print("\nInformation about the test dataset:")
    print(test_df.info())
    
    print("\nSummary statistics of the test dataset:")
    print(test_df.describe())
    
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    # Identify missing values
    print("\nMissing values in the training dataset:")
    print(train_df.isnull().sum())
    
    print("\nMissing values in the test dataset:")
    print(test_df.isnull().sum())
    
    # Visualize missing values using a heatmap
    plt.figure(figsize=(12, 6))
    sns.heatmap(train_df.isnull(), cbar=False, cmap='viridis')
    plt.title('Missing Values in Training Dataset')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/missing_values_train.png')
    plt.show()
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(test_df.isnull(), cbar=False, cmap='viridis')
    plt.title('Missing Values in Test Dataset')
    plt.savefig('/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/missing_values_test.png')
    plt.show()
    
    
    # Explore categorical features
    categorical_features = ['Sex', 'Embarked', 'Pclass']
    
    for feature in categorical_features:
        print(f"\nDistribution of {feature} in the training dataset:")
        print(train_df[feature].value_counts())
        
        plt.figure(figsize=(8, 4))
        sns.countplot(data=train_df, x=feature)
        plt.title(f'Distribution of {feature} in Training Dataset')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/{feature}_distribution_train.png')
        plt.show()
    
    
    # Explore numerical features
    numerical_features = ['Age', 'Fare', 'SibSp', 'Parch']
    
    for feature in numerical_features:
        plt.figure(figsize=(8, 4))
        train_df[feature].hist(bins=30)
        plt.title(f'Distribution of {feature} in Training Dataset')
        plt.xlabel(feature)
        plt.ylabel('Frequency')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/{feature}_histogram_train.png')
        plt.show()
        
        plt.figure(figsize=(8, 4))
        sns.boxplot(data=train_df, x=feature)
        plt.title(f'Box Plot of {feature} in Training Dataset')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/{feature}_boxplot_train.png')
        plt.show()
    
    
    # Examine relationships between features and the target variable
    for feature in categorical_features:
        print(f"\nSurvival rate by {feature}:")
        print(train_df[[feature, 'Survived']].groupby(feature).mean())
        
        plt.figure(figsize=(8, 4))
        sns.barplot(data=train_df, x=feature, y='Survived')
        plt.title(f'Survival Rate by {feature}')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/survival_rate_by_{feature}.png')
        plt.show()
    
    # Scatter plots for numerical features
    for feature in numerical_features:
        plt.figure(figsize=(8, 4))
        sns.scatterplot(data=train_df, x=feature, y='Survived')
        plt.title(f'Survival by {feature}')
        plt.savefig(f'/mnt/d/PythonProjects/AutoKaggleMaster/multi_agents/competition/titanic/pre_eda/images/survival_by_{feature}.png')
        plt.show()
    


if __name__ == "__main__":
    generated_code_function()