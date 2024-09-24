## fill_missing_values

**Name:** fill_missing_values  
**Description:** Fill missing values in specified columns of a DataFrame. This tool can handle both numerical and categorical features by using different filling methods.  
**Applicable Situations:** handle missing values in various types of features

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** The name(s) of the column(s) where missing values should be filled.
- `method`:
  - **Type:** `string`
  - **Description:** The method to use for filling missing values.
  - **Enum:** `auto` | `mean` | `median` | `mode` | `constant`
  - **Default:** `auto`
- `fill_value`:
  - **Type:** ``number` | `string` | `null``
  - **Description:** The value to use when method is 'constant'.
  - **Default:** `None`

**Required:** `data`, `columns`  
**Result:** Successfully fill missing values in the specified column(s) of data  
**Notes:**
- The 'auto' method uses mean for numeric columns and mode for non-numeric columns.
- Using 'mean' or 'median' on non-numeric columns will raise an error.
- The 'mode' method uses the most frequent value, which may not always be appropriate.
- Filling missing values can introduce bias, especially if the data is not missing completely at random.
- Consider the impact of filling missing values on your analysis and model performance.

---
## remove_columns_with_missing_data

**Name:** remove_columns_with_missing_data  
**Description:** Remove columns containing excessive missing values from a DataFrame based on a threshold. This tool provides a flexible way to clean datasets by removing columns with too many missing values, adaptable to different dataset sizes.  
**Applicable Situations:** remove columns with excessive missing values from a dataset

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset.
- `thresh`:
  - **Type:** `number`
  - **Description:** The minimum proportion of missing values required to drop a column. Should be between 0 and 1.
  - **Default:** `0.5`
- `columns`:
  - **Type:** ``string` | `array` | `null``
  - **Description:** Labels of columns to consider. If not specified, all columns will be considered.
  - **Default:** `None`

**Required:** `data`  
**Result:** Successfully remove columns containing excessive missing values from the DataFrame  
**Notes:**
- This method modifies the structure of your dataset by removing entire columns.
- Setting a low threshold might result in loss of important features.
- Setting a high threshold might retain columns with too many missing values.
- Consider the impact of removing columns on your analysis and model performance.
- It's often better to understand why data is missing before deciding to remove it.

---
## detect_and_handle_outliers_zscore

**Name:** detect_and_handle_outliers_zscore  
**Description:** Detect and handle outliers in specified columns using the Z-score method. This tool is useful for identifying and managing extreme values in numerical features based on their distance from the mean in terms of standard deviations.  
**Applicable Situations:** detect and handle outliers in numerical features, especially when the data is approximately normally distributed and the sample size is large

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** The name(s) of the column(s) to check for outliers.
- `threshold`:
  - **Type:** `number`
  - **Description:** The Z-score threshold to identify outliers. Values with absolute Z-scores above this threshold are considered outliers. Typically 3.0 or 2.5.
  - **Default:** `3.0`
- `method`:
  - **Type:** `string`
  - **Description:** The method to handle outliers.
  - **Enum:** `clip` | `remove`
  - **Default:** `clip`

**Required:** `data`, `columns`  
**Result:** Successfully detect and handle outliers in the specified column(s) of data  
**Notes:**
- This method assumes the data is approximately normally distributed.
- It may be sensitive to extreme outliers as they can affect the mean and standard deviation.
- Not suitable for highly skewed distributions.
- The choice of threshold affects the sensitivity of outlier detection.

---
## detect_and_handle_outliers_iqr

**Name:** detect_and_handle_outliers_iqr  
**Description:** Detect and handle outliers in specified columns using the Interquartile Range (IQR) method. This tool is useful for identifying and managing extreme values in numerical features without assuming a specific distribution of the data.  
**Applicable Situations:** detect and handle outliers in numerical features, especially when the data distribution is unknown, non-normal, or when the dataset is small or contains extreme outliers

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** The name(s) of the column(s) to check for outliers.
- `factor`:
  - **Type:** `number`
  - **Description:** The IQR factor to determine the outlier threshold. Typically 1.5 for outliers or 3 for extreme outliers.
  - **Default:** `1.5`
- `method`:
  - **Type:** `string`
  - **Description:** The method to handle outliers.
  - **Enum:** `clip` | `remove`
  - **Default:** `clip`
- `return_mask`:
  - **Type:** `boolean`
  - **Description:** If True, return a boolean mask indicating outliers instead of removing them.
  - **Default:** `False`

**Required:** `data`, `columns`  
**Result:** Successfully detect and handle outliers in the specified column(s) of data using the IQR method  
**Notes:**
- This method does not assume any specific data distribution.
- It is less sensitive to extreme outliers compared to the Z-score method.
- May be less precise for normally distributed data compared to the Z-score method.
- The choice of factor affects the range of what is considered an outlier.
- Using the 'remove' method may delete data entries, which is not recommended for test sets.

---
## remove_duplicates

**Name:** remove_duplicates  
**Description:** Remove duplicate rows from a DataFrame. This tool provides flexible options for identifying and handling duplicate entries in a dataset.  
**Applicable Situations:** remove duplicate entries from a dataset, especially when dealing with data that may have been entered multiple times or when consolidating data from multiple sources

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset.
- `columns`:
  - **Type:** ``string` | `array` | `null``
  - **Description:** Column label or sequence of labels to consider for identifying duplicates. If None, use all columns.
  - **Default:** `None`
- `keep`:
  - **Type:** `string`
  - **Description:** Determines which duplicates (if any) to keep.
  - **Enum:** `first` | `last` | `False`
  - **Default:** `first`
- `inplace`:
  - **Type:** `boolean`
  - **Description:** Whether to drop duplicates in place or return a copy.
  - **Default:** `False`

**Required:** `data`  
**Result:** Successfully remove duplicate rows from the DataFrame  
**Notes:**
- If 'columns' is None, all columns are used for identifying duplicates.
- The 'keep' parameter determines which duplicate rows are retained.
- Setting 'inplace' to True will modify the original DataFrame.
- Be cautious when removing duplicates, as it may affect the integrity of your dataset.
- Consider the impact of removing duplicates on your analysis and model performance.
- This method is useful for data cleaning, but make sure you understand why duplicates exist before removing them.

---
## convert_data_types

**Name:** convert_data_types  
**Description:** Convert the data type of specified columns in a DataFrame. This tool is useful for ensuring data consistency and preparing data for analysis or modeling.  
**Applicable Situations:** data type conversion, data preprocessing, ensuring data consistency across columns

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or sequence of labels to convert.
- `target_type`:
  - **Type:** `string`
  - **Description:** The target data type to convert to.
  - **Enum:** `int` | `float` | `str` | `bool` | `datetime`

**Required:** `data`, `columns`, `target_type`  
**Result:** Successfully convert the data type of specified column(s) in the DataFrame  
**Notes:**
- For 'int' and 'float' conversions, non-numeric values will be converted to NaN.
- The 'int' conversion uses the 'Int64' type, which supports NaN values.
- The 'datetime' conversion will set invalid date/time values to NaT (Not a Time).
- The 'bool' conversion may produce unexpected results for non-boolean data.
- Consider the impact of type conversion on your data analysis and model performance.
- Always verify the results after conversion to ensure data integrity.

---
## format_datetime

**Name:** format_datetime  
**Description:** Format datetime columns in a DataFrame to a specified format. This tool is useful for standardizing date and time representations across your dataset.  
**Applicable Situations:** datetime standardization, data preprocessing, ensuring consistent datetime formats

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or sequence of labels to format.
- `format`:
  - **Type:** `string`
  - **Description:** The desired output format for datetime.
  - **Default:** `%Y-%m-%d %H:%M:%S`
- `errors`:
  - **Type:** `string`
  - **Description:** How to handle parsing errors.
  - **Enum:** `raise` | `coerce` | `ignore`
  - **Default:** `coerce`

**Required:** `data`, `columns`  
**Result:** Successfully format the datetime columns in the DataFrame  
**Notes:**
- The method first converts the specified columns to datetime using pd.to_datetime before formatting.
- The 'format' parameter uses Python's strftime and strptime format codes.
- When 'errors' is set to 'coerce', invalid parsing will be set to NaT (Not a Time).
- When 'errors' is set to 'ignore', invalid parsing will return the input.
- When 'errors' is set to 'raise', invalid parsing will raise an exception.
- Ensure that the specified format matches the expected datetime structure in your data.
- Consider the impact of datetime formatting on your data analysis and model performance.

---
## one_hot_encode

**Name:** one_hot_encode  
**Description:** Perform one-hot encoding on specified categorical columns of a DataFrame.  
**Applicable Situations:** Encoding categorical variables with no ordinal relationship, especially useful for machine learning models that cannot handle categorical data directly (e.g., linear regression, neural networks). Best for categorical variables with relatively few unique categories.

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** The input DataFrame containing categorical columns to be encoded.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or list of column labels to encode.
- `drop_original`:
  - **Type:** `boolean`
  - **Description:** Whether to drop the original columns after encoding.
  - **Default:** `True`
- `handle_unknown`:
  - **Type:** `string`
  - **Description:** How to handle unknown categories during transform.
  - **Enum:** `error` | `ignore`
  - **Default:** `error`

**Required:** `data`, `columns`  
**Result:** DataFrame with one-hot encoded columns  
**Notes:**
- One-hot encoding creates a new binary column for each category in the original column.
- It can significantly increase the number of features, especially for columns with many unique categories.
- May lead to the 'curse of dimensionality' if used on high-cardinality categorical variables.
- Suitable for nominal categorical data where there's no inherent order among categories.
- The function will raise a warning if applied to non-categorical columns.
- Setting handle_unknown='ignore' will create an all-zero row for unknown categories during transform.
- Consider using other encoding methods for high-cardinality features to avoid dimensionality issues.
**Example:**
  - **Input:**
    - `data`: {'color': ['red', 'blue', 'green', 'red']}
    - `columns`: color
  - **Output:**
    - `color_blue`: [0, 1, 0, 0]
    - `color_green`: [0, 0, 1, 0]
    - `color_red`: [1, 0, 0, 1]

---
## label_encode

**Name:** label_encode  
**Description:** Perform label encoding on specified categorical columns of a DataFrame.  
**Applicable Situations:** Encoding categorical variables with an ordinal relationship, or when the number of categories is large and one-hot encoding would lead to too many features. Useful for tree-based models that can handle categorical data.

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** The input DataFrame containing categorical columns to be encoded.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or list of column labels to encode.
- `drop_original`:
  - **Type:** `boolean`
  - **Description:** Whether to drop the original columns after encoding.
  - **Default:** `True`

**Required:** `data`, `columns`  
**Result:** DataFrame with label encoded columns  
**Notes:**
- Label encoding assigns a unique integer to each category based on alphabetical order.
- It preserves memory compared to one-hot encoding, especially for high-cardinality features.
- Suitable for ordinal categorical data where there's a clear order among categories.
- May introduce an ordinal relationship where none exists, which can be problematic for some models.
- The function will raise a warning if applied to non-categorical columns.
- Tree-based models can often handle label-encoded categorical variables well.
- Be cautious when using with linear models, as they may interpret the labels as having an ordinal relationship.
**Example:**
  - **Input:**
    - `data`: {'fruit': ['apple', 'banana', 'apple', 'cherry']}
    - `columns`: fruit
  - **Output:**
    - `fruit_encoded`: [0, 1, 0, 2]

---
## frequency_encode

**Name:** frequency_encode  
**Description:** Perform frequency encoding on specified categorical columns of a DataFrame.  
**Applicable Situations:** Encoding high-cardinality categorical variables, especially when the frequency of categories is informative. Useful for both tree-based and linear models.

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** The input DataFrame containing categorical columns to be encoded.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or list of column labels to encode.
- `drop_original`:
  - **Type:** `boolean`
  - **Description:** Whether to drop the original columns after encoding.
  - **Default:** `True`

**Required:** `data`, `columns`  
**Result:** DataFrame with frequency encoded columns  
**Notes:**
- Frequency encoding replaces each category with its relative frequency in the dataset.
- It can capture some information about the importance of each category.
- Useful for high-cardinality categorical variables where one-hot encoding would create too many features.
- Preserves information about the distribution of categories.
- May be particularly useful when the frequency of a category is informative for the target variable.
- The function will raise a warning if applied to non-categorical columns.
- Be aware that this method can potentially introduce a false sense of ordinality among categories.
**Example:**
  - **Input:**
    - `data`: {'city': ['New York', 'London', 'Paris', 'New York', 'London', 'New York']}
    - `columns`: city
  - **Output:**
    - `city_freq`: [0.5, 0.33, 0.17, 0.5, 0.33, 0.5]

---
## target_encode

**Name:** target_encode  
**Description:** Perform target encoding on specified categorical columns of a DataFrame.  
**Applicable Situations:** Encoding categorical variables in supervised learning tasks, especially effective for high-cardinality features. Useful when there's a clear relationship between categories and the target variable.

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** The input DataFrame containing categorical columns to be encoded and the target variable.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or list of column labels to encode.
- `target`:
  - **Type:** `string`
  - **Description:** The name of the target column in the DataFrame.
- `drop_original`:
  - **Type:** `boolean`
  - **Description:** Whether to drop the original columns after encoding.
  - **Default:** `True`
- `min_samples_leaf`:
  - **Type:** `integer`
  - **Description:** Minimum samples to take category average into account.
  - **Default:** `1`
- `smoothing`:
  - **Type:** `number`
  - **Description:** Smoothing effect to balance categorical average vs prior.
  - **Default:** `1.0`

**Required:** `data`, `columns`, `target`  
**Result:** DataFrame with target encoded columns  
**Notes:**
- Target encoding replaces a categorical value with the mean of the target variable for that value.
- It can capture complex relationships between categorical variables and the target.
- Particularly useful for high-cardinality categorical variables in supervised learning tasks.
- The smoothing parameter helps prevent overfitting, especially for categories with few samples.
- Be cautious of potential data leakage; consider using cross-validation techniques for encoding.
- The function will raise a warning if applied to non-categorical columns.
- This method can be sensitive to outliers in the target variable.
- Consider the impact of target encoding on model interpretability.
**Example:**
  - **Input:**
    - `data`: {'category': ['A', 'B', 'A', 'C', 'B', 'A'], 'target': [1, 0, 1, 1, 0, 0]}
    - `columns`: category
    - `target`: target
  - **Output:**
    - `category_target_enc`: [0.5, 0.0, 0.5, 1.0, 0.0, 0.5]

---
## correlation_feature_selection

**Name:** correlation_feature_selection  
**Description:** Perform feature selection based on correlation analysis. This tool helps identify features that have a strong correlation with the target variable.  
**Applicable Situations:** feature selection, dimensionality reduction, identifying important features for predictive modeling

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset, including features and target.
- `target`:
  - **Type:** `string`
  - **Description:** The name of the target column in the DataFrame.
- `method`:
  - **Type:** `string`
  - **Description:** The correlation method to use.
  - **Enum:** `pearson` | `spearman` | `kendall`
  - **Default:** `pearson`
- `threshold`:
  - **Type:** `number`
  - **Description:** The correlation threshold for feature selection. Features with absolute correlation greater than this value will be selected.
  - **Default:** `0.5`

**Required:** `data`, `target`  
**Result:** DataFrame with selected features and their correlation with the target  
**Notes:**
- Pearson correlation assumes a linear relationship and is sensitive to outliers.
- Spearman correlation is rank-based and can capture monotonic relationships.
- Kendall correlation is another rank-based method, often used for small sample sizes.
- This method is most suitable for numerical features and targets.
- Be cautious with high correlations between features (multicollinearity).
- Consider the domain knowledge when interpreting the results and selecting features.
- This method does not account for interactions between features or non-linear relationships with the target.

---
## variance_feature_selection

**Name:** variance_feature_selection  
**Description:** Perform feature selection based on variance analysis. This tool helps identify and remove features with low variance, which often contribute little to model performance.  
**Applicable Situations:** feature selection, dimensionality reduction, removing constant or near-constant features

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset with features.
- `threshold`:
  - **Type:** `number`
  - **Description:** Features with a variance lower than this threshold will be removed.
  - **Default:** `0.0`
- `columns`:
  - **Type:** ``string` | `array` | `null``
  - **Description:** Column label or sequence of labels to consider. If None, use all columns.
  - **Default:** `None`

**Required:** `data`  
**Result:** DataFrame with selected features and their variances  
**Notes:**
- This method is most suitable for numerical features.
- A threshold of 0.0 will remove features that are constant across all samples.
- For binary features, a threshold of 0.8 * (1 - 0.8) = 0.16 would remove features that have the same value in more than 80% of the samples.
- Consider scaling your features before applying this method if they are on different scales.
- This method does not consider the relationship between features and the target variable.
- Be cautious when using this method with small datasets, as variance estimates may be unreliable.
- Features with high variance are not necessarily informative; consider combining this method with other feature selection techniques.

---
## scale_features

**Name:** scale_features  
**Description:** Scale numerical features in the specified columns of a DataFrame using various scaling methods.  
**Applicable Situations:** feature scaling for numerical data, data preprocessing for numerical features, preparing numerical data for machine learning models that are sensitive to the scale of input features (e.g., neural networks, SVM, K-means clustering)

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset with numerical features to be scaled.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or sequence of labels of numerical features to scale.
- `method`:
  - **Type:** `string`
  - **Description:** The scaling method to use.
  - **Enum:** `standard` | `minmax` | `robust`
  - **Default:** `standard`
- `copy`:
  - **Type:** `boolean`
  - **Description:** If False, try to avoid a copy and do inplace scaling instead.
  - **Default:** `True`

**Required:** `data`, `columns`  
**Result:** DataFrame with scaled features  
**Notes:**
- This function is designed for numerical features only. It should not be used on categorical data.
- StandardScaler: Standardizes features by removing the mean and scaling to unit variance.
- MinMaxScaler: Scales features to a given range, usually between 0 and 1.
- RobustScaler: Scales features using statistics that are robust to outliers.
- Scaling is sensitive to the presence of outliers, especially for StandardScaler and MinMaxScaler.
- RobustScaler is a good choice when your data contains many outliers.
- Scaling should typically be done after splitting your data into training and test sets to avoid data leakage.
- For categorical data, consider using encoding techniques instead of scaling.

---
## perform_pca

**Name:** perform_pca  
**Description:** Perform Principal Component Analysis (PCA) on specified columns of a DataFrame. This tool is useful for dimensionality reduction, feature extraction, and data visualization.  
**Applicable Situations:** dimensionality reduction, feature extraction, data visualization, handling multicollinearity

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset with features.
- `n_components`:
  - **Type:** ``integer` | `number` | `string``
  - **Description:** Number of components to keep. If int, it represents the exact number of components. If float between 0 and 1, it represents the proportion of variance to be retained. If 'mle', Minka's MLE is used to guess the dimension.
  - **Default:** `0.95`
- `columns`:
  - **Type:** ``string` | `array` | `null``
  - **Description:** Column label or sequence of labels to consider. If None, use all columns.
  - **Default:** `None`
- `scale`:
  - **Type:** `boolean`
  - **Description:** Whether to scale the data before applying PCA. Recommended when features are not on the same scale.
  - **Default:** `True`

**Required:** `data`  
**Result:** DataFrame with PCA results  
**Notes:**
- PCA assumes linear relationships between features.
- It's sensitive to the scale of the features, so scaling is often recommended.
- PCA may not be suitable for categorical data or when preserving feature interpretability is crucial.
- The number of components to keep is a trade-off between dimensionality reduction and information retention.
- Consider visualizing the cumulative explained variance to choose an appropriate number of components.
- PCA can help address multicollinearity in regression problems.
- The resulting principal components are orthogonal (uncorrelated) to each other.
- The function now returns only the DataFrame with PCA results, without additional information about explained variance or the PCA model.
**Example:**
  - **Input:**
    - `data`: {'feature1': [1, 2, 3, 4, 5], 'feature2': [2, 4, 5, 4, 5], 'feature3': [3, 6, 7, 8, 9]}
    - `n_components`: 2
  - **Output:**
    - `PC1`: [-2.12132, -0.707107, 0.0, 0.707107, 2.12132]
    - `PC2`: [-0.707107, 0.707107, 0.0, -0.707107, 0.707107]

---
## perform_rfe

**Name:** perform_rfe  
**Description:** Perform Recursive Feature Elimination (RFE) on specified columns of a DataFrame. This tool is useful for feature selection, especially when dealing with high-dimensional data.  
**Applicable Situations:** feature selection, dimensionality reduction, identifying important features for predictive modeling

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** A pandas DataFrame object representing the dataset with features.
- `target`:
  - **Type:** ``string` | `pd.Series``
  - **Description:** The target variable. If string, it should be the name of the target column in data.
- `n_features_to_select`:
  - **Type:** ``integer` | `number``
  - **Description:** Number of features to select. If int, it represents the exact number of features. If float between 0 and 1, it represents the proportion of features to select.
  - **Default:** `0.5`
- `step`:
  - **Type:** `integer`
  - **Description:** Number of features to remove at each iteration.
  - **Default:** `1`
- `estimator`:
  - **Type:** `string`
  - **Description:** The estimator to use for feature importance ranking.
  - **Enum:** `auto` | `logistic` | `rf` | `linear` | `rf_regressor`
  - **Default:** `auto`
- `columns`:
  - **Type:** ``string` | `array` | `null``
  - **Description:** Column label or sequence of labels to consider. If None, use all columns except the target (if target is a column name in data).
  - **Default:** `None`

**Required:** `data`, `target`  
**Result:** DataFrame with selected features  
**Notes:**
- RFE is computationally expensive, especially with a large number of features.
- The choice of estimator can significantly affect the results.
- The 'auto' estimator option will automatically choose based on the target variable type.
- RFE does not consider interactions between features.
- The step parameter can be increased to speed up the process, but may result in less optimal feature selection.
- Consider cross-validation for more robust feature selection.
- The selected features may not always be the optimal set for all models or tasks.
- RFE assumes that the importance of a feature is reflected in the magnitude of its coefficient or feature importance score.
- The function returns only the DataFrame with selected features, without additional information about feature rankings or the RFE model.

---
## create_polynomial_features

**Name:** create_polynomial_features  
**Description:** Create polynomial features from specified numerical columns of a DataFrame.  
**Applicable Situations:** Capturing non-linear relationships between features and the target variable. Useful for linear models to learn non-linear patterns, or for enhancing the feature space of any model when non-linear interactions are suspected.

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** The input DataFrame containing numerical columns for polynomial feature creation.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or list of column labels to use for creating polynomial features.
- `degree`:
  - **Type:** `integer`
  - **Description:** The degree of the polynomial features.
  - **Default:** `2`
- `interaction_only`:
  - **Type:** `boolean`
  - **Description:** If True, only interaction features are produced.
  - **Default:** `False`
- `include_bias`:
  - **Type:** `boolean`
  - **Description:** If True, include a bias column (all 1s).
  - **Default:** `False`

**Required:** `data`, `columns`  
**Result:** DataFrame with original and new polynomial features  
**Notes:**
- Only works with numerical features. Will raise an error if non-numeric columns are specified.
- Can significantly increase the number of features, potentially leading to overfitting or computational issues.
- Higher degrees capture more complex non-linear relationships but increase the risk of overfitting.
- Consider using regularization techniques when using polynomial features with linear models.
- The function will warn if the resulting DataFrame has over 1000 columns.
- Polynomial features can be particularly useful for regression problems or for capturing complex interactions in classification tasks.
- Be cautious of multicollinearity when using polynomial features, especially with high degrees.

---
## create_feature_combinations

**Name:** create_feature_combinations  
**Description:** Create feature combinations from specified numerical columns of a DataFrame.  
**Applicable Situations:** Capturing interactions between features that may be important for the target variable. Useful for both linear and non-linear models to learn from feature interactions.

**Parameters:**
- `data`:
  - **Type:** `pd.DataFrame`
  - **Description:** The input DataFrame containing numerical columns for feature combination.
- `columns`:
  - **Type:** ``string` | `array``
  - **Description:** Column label or list of column labels to use for creating feature combinations.
- `combination_type`:
  - **Type:** `string`
  - **Description:** Type of combination to create.
  - **Enum:** `multiplication` | `addition`
  - **Default:** `multiplication`
- `max_combination_size`:
  - **Type:** `integer`
  - **Description:** Maximum number of features to combine.
  - **Default:** `2`

**Required:** `data`, `columns`  
**Result:** DataFrame with original and new combined features  
**Notes:**
- Only works with numerical features. Will raise an error if non-numeric columns are specified.
- Can significantly increase the number of features, potentially leading to overfitting or computational issues.
- Multiplication combinations are useful for capturing non-linear interactions.
- Addition combinations can be useful for creating aggregate features.
- The function will warn if the resulting DataFrame has over 1000 columns.
- Consider the interpretability of the resulting features, especially with high-order combinations.
- Feature combinations can help in discovering complex patterns that individual features might not capture.
- Be mindful of the computational cost, especially with a large number of input features or high max_combination_size.

---
## model_choice

**Name:** model_choice  
**Description:** Choose a machine learning model based on the input model name.  
**Applicable Situations:** Model selection for various machine learning tasks, ensuring the use of appropriate algorithms based on the problem type.

**Parameters:**
- `model_name`:
  - **Type:** `string`
  - **Description:** The name of the model to choose.
  - **Enum:** `linear regression` | `logistic regression` | `decision tree` | `random forest` | `XGBoost` | `SVM` | `neural network`

**Required:** `model_name`  
**Result:** Model instance corresponding to the selected model name.  
**Notes:**
- Facilitates the selection of compatible scikit-learn models.
- Ensure that the model_name is valid to avoid runtime errors.

---
## model_train

**Name:** model_train  
**Description:** Choose a model training tool based on the input training tool name.  
**Applicable Situations:** Model training and optimization processes, allowing users to select appropriate techniques for hyperparameter tuning.

**Parameters:**
- `train_tool`:
  - **Type:** `string`
  - **Description:** The name of the model training tool.
  - **Enum:** `cross validation` | `grid search` | `random search`

**Required:** `train_tool`  
**Result:** The corresponding training tool instance.  
**Notes:**
- Supports efficient model evaluation and parameter tuning.
- Choose training tools based on model complexity and data characteristics.

---
## model_evaluation

**Name:** model_evaluation  
**Description:** Choose a model evaluation tool based on the input evaluation tool name.  
**Applicable Situations:** Model performance assessment for classification and regression tasks.

**Parameters:**
- `evaluation_tool`:
  - **Type:** `string`
  - **Description:** The name of the evaluation tool.
  - **Enum:** `accuracy` | `precision` | `recall` | `F1 score` | `ROC AUC` | `MSE` | `RMSE` | `MAE` | `R²`

**Required:** `evaluation_tool`  
**Result:** Corresponding evaluation function for the selected metric.  
**Notes:**
- Supports both classification and regression evaluation metrics.
- Ensure compatibility of the chosen metric with the model type.

---
## model_explanation

**Name:** model_explanation  
**Description:** Choose a model explanation tool based on the input tool name.  
**Applicable Situations:** Understanding model behavior and feature contributions in predictive models.

**Parameters:**
- `explanation_tool`:
  - **Type:** `string`
  - **Description:** The name of the explanation tool.
  - **Enum:** `feature importance` | `SHAP` | `partial dependence`

**Required:** `explanation_tool`  
**Result:** Corresponding explanation function for the selected tool.  
**Notes:**
- Provides insights into model predictions and feature significance.
- Select tools based on the model type and interpretability needs.

---
## model_persistence

**Name:** model_persistence  
**Description:** Choose a model persistence tool for saving and loading models.  
**Applicable Situations:** Model serialization and deserialization for long-term storage and retrieval.

**Parameters:**
- `tool_name`:
  - **Type:** `string`
  - **Description:** The name of the persistence tool.
  - **Enum:** `joblib` | `pickle`

**Required:** `tool_name`  
**Result:** A dictionary with 'save' and 'load' functions for the chosen tool.  
**Notes:**
- Select the persistence tool based on the complexity and size of the model.
- Ensure compatibility with the model type when saving and loading.

---
## prediction_tool

**Name:** prediction_tool  
**Description:** Choose a prediction tool for single or batch predictions.  
**Applicable Situations:** Making predictions using trained models for either individual samples or multiple samples.

**Parameters:**
- `tool_name`:
  - **Type:** `string`
  - **Description:** The name of the prediction tool.
  - **Enum:** `single prediction` | `batch prediction`
- `model`:
  - **Type:** `object`
  - **Description:** The trained model to use for predictions.
- `X`:
  - **Type:** `array`
  - **Description:** The input data for prediction, either a single sample or batch of samples.

**Required:** `tool_name`, `model`, `X`  
**Result:** The predictions made by the model as a numpy array.  
**Notes:**
- Choose the prediction tool based on the data format and requirements.
- Ensure that the input data matches the model's expected input shape.

---
## best_model_selection_tool

**Name:** best_model_selection_tool  
**Description:** Choose the best model based on a specific evaluation metric.  
**Applicable Situations:** Model evaluation and selection based on performance metrics for classification or regression tasks.

**Parameters:**
- `tool_name`:
  - **Type:** `string`
  - **Description:** The name of the model selection tool.
  - **Enum:** `classification` | `regression`
- `model_paths`:
  - **Type:** `array`
  - **Description:** A list of file paths to the trained models.
- `persistence_tool`:
  - **Type:** `string`
  - **Description:** The model persistence tool.
  - **Enum:** `joblib` | `pickle`
- `X_test`:
  - **Type:** `array`
  - **Description:** The test input data.
- `y_test`:
  - **Type:** `array`
  - **Description:** The test target labels.
- `evaluation_tool`:
  - **Type:** `string`
  - **Description:** The name of the evaluation metric to use.

**Required:** `tool_name`, `model_paths`, `persistence_tool`, `X_test`, `y_test`, `evaluation_tool`  
**Result:** Tuple containing the best model and its evaluation score.  
**Notes:**
- Evaluates multiple models to find the best based on the specified metric.
- Ensure that models are compatible with the chosen evaluation metric.

---
## ensemble_model_tool

**Name:** ensemble_model_tool  
**Description:** Choose an ensemble learning tool based on the input tool name.  
**Applicable Situations:** Creating ensemble models for improved predictive performance using Bagging, Boosting, or Stacking techniques.

**Parameters:**
- `tool_name`:
  - **Type:** `string`
  - **Description:** The name of the ensemble learning tool.
  - **Enum:** `Bagging` | `Boosting` | `Stacking`
- `base_estimator`:
  - **Type:** `object`
  - **Description:** The base estimator for Bagging (default: None).
- `estimators`:
  - **Type:** `array`
  - **Description:** List of estimators for Stacking (default: None).

**Required:** `tool_name`, `base_estimator`, `estimators`  
**Result:** An instance of the corresponding ensemble learning tool.  
**Notes:**
- Select the appropriate ensemble method based on the problem context.
- Consider base estimators for Bagging to improve model performance.

---
## hyperparameter_optimization_tool

**Name:** hyperparameter_optimization_tool  
**Description:** Choose a hyperparameter optimization tool based on the input tool name.  
**Applicable Situations:** Optimizing model parameters to improve performance using various search techniques.

**Parameters:**
- `tool_name`:
  - **Type:** `string`
  - **Description:** The name of the optimization tool.
  - **Enum:** `Grid Search` | `Random Search` | `Bayesian Optimization`
- `model`:
  - **Type:** `object`
  - **Description:** The machine learning model to optimize.
- `param_grid`:
  - **Type:** `object`
  - **Description:** The parameter grid to search over.
- `X`:
  - **Type:** `object`
  - **Description:** Training data features as a pandas DataFrame.
- `y`:
  - **Type:** `object`
  - **Description:** Training data labels as a pandas Series.
- `cv`:
  - **Type:** `integer`
  - **Description:** Number of cross-validation folds.
  - **Default:** `5`
- `n_iter`:
  - **Type:** `integer`
  - **Description:** Number of iterations for Random Search or Bayesian Optimization.
  - **Default:** `10`

**Required:** `tool_name`, `model`, `param_grid`, `X`, `y`, `cv`, `n_iter`  
**Result:** Optimized model after performing the selected hyperparameter search.  
**Notes:**
- Select an optimization method based on the problem's complexity and the model's characteristics.
- Consider the trade-off between search time and the quality of the found parameters.

---
