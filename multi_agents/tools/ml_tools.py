import pandas as pd
import numpy as np
from typing import Dict, Any, Union, List
from scipy.stats import spearmanr
from sklearn.feature_selection import VarianceThreshold, RFE
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder, LabelEncoder, PolynomialFeatures
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from itertools import combinations
import warnings

def fill_missing_values(data: pd.DataFrame, columns: Union[str, List[str]], method: str = 'auto', fill_value: Any = None) -> pd.DataFrame:
    """
    Fill missing values in specified columns of a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): The name(s) of the column(s) to fill missing values.
        method (str, optional): The method to use for filling missing values. 
            Options: 'auto', 'mean', 'median', 'mode', 'constant'. Defaults to 'auto'.
        fill_value (Any, optional): The value to use when method is 'constant'. Defaults to None.

    Returns:
        pd.DataFrame: The DataFrame with filled missing values.
    """
    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        if method == 'auto':
            if pd.api.types.is_numeric_dtype(data[column]):
                data[column].fillna(data[column].mean(), inplace=True)
            else:
                data[column].fillna(data[column].mode()[0], inplace=True)
        elif method == 'mean':
            data[column].fillna(data[column].mean(), inplace=True)
        elif method == 'median':
            data[column].fillna(data[column].median(), inplace=True)
        elif method == 'mode':
            data[column].fillna(data[column].mode()[0], inplace=True)
        elif method == 'constant':
            data[column].fillna(fill_value, inplace=True)
        else:
            raise ValueError("Invalid method. Choose from 'auto', 'mean', 'median', 'mode', or 'constant'.")

    return data

def remove_columns_with_missing_data(data: pd.DataFrame, thresh: float = 0.5, columns: Union[str, List[str]] = None) -> pd.DataFrame:
    """
    Remove columns containing missing values from a DataFrame based on a threshold.

    Args:
        data (pd.DataFrame): The input DataFrame.
        thresh (float, optional): The minimum proportion of missing values required to drop a column. 
                                    Should be between 0 and 1. Defaults to 0.5.
        columns (str or List[str], optional): Labels of columns to consider. Defaults to None.

    Returns:
        pd.DataFrame: The DataFrame with columns containing excessive missing values removed.
    """
    if not 0 <= thresh <= 1:
        raise ValueError("thresh must be between 0 and 1")

    if columns is not None:
        if isinstance(columns, str):
            columns = [columns]
        data_subset = data[columns]
    else:
        data_subset = data

    # Calculate the number of missing values allowed based on the threshold
    max_missing = int(thresh * len(data_subset))

    # Identify columns to keep
    columns_to_keep = data_subset.columns[data_subset.isna().sum() < max_missing]

    # If columns was specified, add back other columns not in the subset
    if columns is not None:
        columns_to_keep = columns_to_keep.union(data.columns.difference(columns))

    return data[columns_to_keep]

def detect_and_handle_outliers_zscore(data: pd.DataFrame, columns: Union[str, List[str]], threshold: float = 3.0, method: str = 'clip') -> pd.DataFrame:
    """
    Detect and handle outliers in specified columns using the Z-score method.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): The name(s) of the column(s) to check for outliers.
        threshold (float, optional): The Z-score threshold to identify outliers. Defaults to 3.0.
        method (str, optional): The method to handle outliers. Options: 'clip', 'remove'. Defaults to 'clip'.

    Returns:
        pd.DataFrame: The DataFrame with outliers handled.
    """
    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        if not pd.api.types.is_numeric_dtype(data[column]):
            raise ValueError(f"Column '{column}' must be numeric.")

        mean = data[column].mean()
        std = data[column].std()
        z_scores = (data[column] - mean) / std

        if method == 'clip':
            lower_bound = mean - threshold * std
            upper_bound = mean + threshold * std
            data[column] = data[column].clip(lower_bound, upper_bound)
        elif method == 'remove':
            data = data[abs(z_scores) <= threshold]
        else:
            raise ValueError("Invalid method. Choose from 'clip' or 'remove'.")

    return data

def detect_and_handle_outliers_iqr(data: pd.DataFrame, columns: Union[str, List[str]], factor: float = 1.5, method: str = 'clip') -> pd.DataFrame:
    """
    Detect and handle outliers in specified columns using the Interquartile Range (IQR) method.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): The name(s) of the column(s) to check for outliers.
        factor (float, optional): The IQR factor to determine the outlier threshold. Defaults to 1.5.
        method (str, optional): The method to handle outliers. Options: 'clip', 'remove'. Defaults to 'clip'.

    Returns:
        pd.DataFrame: The DataFrame with outliers handled.
    """
    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        if not pd.api.types.is_numeric_dtype(data[column]):
            raise ValueError(f"Column '{column}' must be numeric.")

        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR

        if method == 'clip':
            data[column] = data[column].clip(lower_bound, upper_bound)
        elif method == 'remove':
            data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        else:
            raise ValueError("Invalid method. Choose from 'clip' or 'remove'.")

    return data

def remove_duplicates(data: pd.DataFrame, columns: Union[str, List[str]] = None, keep: str = 'first', inplace: bool = False) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str], optional): Column label or sequence of labels to consider for identifying duplicates. 
                                                If None, use all columns. Defaults to None.
        keep (str, optional): Determines which duplicates (if any) to keep.
            - 'first' : Drop duplicates except for the first occurrence.
            - 'last' : Drop duplicates except for the last occurrence.
            - False : Drop all duplicates.
            Defaults to 'first'.
        inplace (bool, optional): Whether to drop duplicates in place or return a copy. Defaults to False.

    Returns:
        pd.DataFrame: The DataFrame with duplicate rows removed.
    """
    if inplace:
        data.drop_duplicates(subset=columns, keep=keep, inplace=True)
        return data
    else:
        return data.drop_duplicates(subset=columns, keep=keep)

def convert_data_types(data: pd.DataFrame, columns: Union[str, List[str]], target_type: str) -> pd.DataFrame:
    """
    Convert the data type of specified columns in a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or sequence of labels to convert.
        target_type (str): The target data type to convert to. 
                            Options: 'int', 'float', 'str', 'bool', 'datetime'.

    Returns:
        pd.DataFrame: The DataFrame with converted data types.
    """
    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in the DataFrame.")

        if target_type == 'int':
            data[column] = pd.to_numeric(data[column], errors='coerce').astype('Int64')
        elif target_type == 'float':
            data[column] = pd.to_numeric(data[column], errors='coerce')
        elif target_type == 'str':
            data[column] = data[column].astype(str)
        elif target_type == 'bool':
            data[column] = data[column].astype(bool)
        elif target_type == 'datetime':
            data[column] = pd.to_datetime(data[column], errors='coerce')
        else:
            raise ValueError("Invalid target_type. Choose from 'int', 'float', 'str', 'bool', or 'datetime'.")

    return data

def format_datetime(data: pd.DataFrame, columns: Union[str, List[str]], format: str = '%Y-%m-%d %H:%M:%S', errors: str = 'coerce') -> pd.DataFrame:
    """
    Format datetime columns in a DataFrame to a specified format.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or sequence of labels to format.
        format (str, optional): The desired output format for datetime. 
                                Defaults to '%Y-%m-%d %H:%M:%S'.
        errors (str, optional): How to handle parsing errors. 
                                Options: 'raise', 'coerce', 'ignore'. Defaults to 'coerce'.

    Returns:
        pd.DataFrame: The DataFrame with formatted datetime columns.
    """
    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in the DataFrame.")

        # First, ensure the column is in datetime format
        data[column] = pd.to_datetime(data[column], errors=errors)

        # Then, format the datetime column
        data[column] = data[column].dt.strftime(format)

    return data

def one_hot_encode(data: pd.DataFrame, 
                   columns: Union[str, List[str]], 
                   drop_original: bool = True, 
                   handle_unknown: str = 'error') -> pd.DataFrame:
    """
    Perform one-hot encoding on specified categorical columns.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or list of column labels to encode.
        drop_original (bool, optional): Whether to drop the original columns. Defaults to True.
        handle_unknown (str, optional): How to handle unknown categories. Options are 'error' or 'ignore'. Defaults to 'error'.

    Returns:
        pd.DataFrame: DataFrame with one-hot encoded columns.

    Raises:
        ValueError: If specified columns are not categorical or if unknown categories are encountered (when handle_unknown='error').
    
    Example:
        >>> df = pd.DataFrame({'color': ['red', 'blue', 'green', 'red']})
        >>> one_hot_encode(df, 'color')
           color_blue  color_green  color_red
        0           0            0          1
        1           1            0          0
        2           0            1          0
        3           0            0          1
    """
    if isinstance(columns, str):
        columns = [columns]

    # Check if specified columns exist and are categorical
    for col in columns:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")
        if not pd.api.types.is_categorical_dtype(data[col]) and not pd.api.types.is_object_dtype(data[col]):
            warnings.warn(f"Column '{col}' is {data[col].dtype}, which is not categorical. One-hot encoding may not be appropriate.")

    # Perform one-hot encoding
    encoder = OneHotEncoder(sparse_output=False, handle_unknown=handle_unknown)
    encoded = encoder.fit_transform(data[columns])
    
    # Create new column names
    new_columns = [f"{col}_{val}" for col, vals in zip(columns, encoder.categories_) for val in vals]
    
    # Create a new DataFrame with encoded values
    encoded_df = pd.DataFrame(encoded, columns=new_columns, index=data.index)
    
    # Combine with original DataFrame
    result = pd.concat([data, encoded_df], axis=1)
    
    # Drop original columns if specified
    if drop_original:
        result = result.drop(columns, axis=1)
    
    return result

def label_encode(data: pd.DataFrame, 
                 columns: Union[str, List[str]], 
                 drop_original: bool = True) -> pd.DataFrame:
    """
    Perform label encoding on specified categorical columns.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or list of column labels to encode.
        drop_original (bool, optional): Whether to drop the original columns. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame with label encoded columns

    Raises:
        ValueError: If specified columns are not found in the DataFrame.

    Example:
        >>> df = pd.DataFrame({'fruit': ['apple', 'banana', 'apple', 'cherry']})
        >>> label_encode(df, 'fruit')
           fruit_encoded
        0              0
        1              1
        2              0
        3              2
    """
    if isinstance(columns, str):
        columns = [columns]

    result = data.copy()

    for col in columns:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")
        if not pd.api.types.is_categorical_dtype(data[col]) and not pd.api.types.is_object_dtype(data[col]):
            warnings.warn(f"Column '{col}' is {data[col].dtype}, which is not categorical. Label encoding may not be appropriate.")

        encoder = LabelEncoder()
        result[f"{col}_encoded"] = encoder.fit_transform(data[col].astype(str))

        if drop_original:
            result = result.drop(col, axis=1)

    return result

def frequency_encode(data: pd.DataFrame, 
                     columns: Union[str, List[str]], 
                     drop_original: bool = True) -> pd.DataFrame:
    """
    Perform frequency encoding on specified categorical columns.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or list of column labels to encode.
        drop_original (bool, optional): Whether to drop the original columns. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame with frequency encoded columns

    Raises:
        ValueError: If specified columns are not found in the DataFrame.

    Example:
        >>> df = pd.DataFrame({'city': ['New York', 'London', 'Paris', 'New York', 'London', 'New York']})
        >>> frequency_encode(df, 'city')
           city_freq
        0       0.50
        1       0.33
        2       0.17
        3       0.50
        4       0.33
        5       0.50
    """
    if isinstance(columns, str):
        columns = [columns]

    result = data.copy()

    for col in columns:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")
        if not pd.api.types.is_categorical_dtype(data[col]) and not pd.api.types.is_object_dtype(data[col]):
            warnings.warn(f"Column '{col}' is {data[col].dtype}, which is not categorical. Frequency encoding may not be appropriate.")

        frequency = data[col].value_counts(normalize=True)
        result[f"{col}_freq"] = data[col].map(frequency)

        if drop_original:
            result = result.drop(col, axis=1)

    return result

def target_encode(data: pd.DataFrame, 
                  columns: Union[str, List[str]], 
                  target: str, 
                  drop_original: bool = True, 
                  min_samples_leaf: int = 1, 
                  smoothing: float = 1.0) -> pd.DataFrame:
    """
    Perform target encoding on specified categorical columns.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or list of column labels to encode.
        target (str): The name of the target column.
        drop_original (bool, optional): Whether to drop the original columns. Defaults to True.
        min_samples_leaf (int, optional): Minimum samples to take category average into account. Defaults to 1.
        smoothing (float, optional): Smoothing effect to balance categorical average vs prior. Defaults to 1.0.

    Returns:
        pd.DataFrame: DataFrame with target encoded columns

    Raises:
        ValueError: If specified columns are not found in the DataFrame or if the target column is not found.
    
    Example:
        >>> df = pd.DataFrame({'category': ['A', 'B', 'A', 'C', 'B', 'A'], 'target': [1, 0, 1, 1, 0, 0]})
        >>> target_encode(df, 'category', 'target')
           category_target_enc
        0              0.5000
        1              0.0000
        2              0.5000
        3              1.0000
        4              0.0000
        5              0.5000
    """
    if isinstance(columns, str):
        columns = [columns]

    if target not in data.columns:
        raise ValueError(f"Target column '{target}' not found in the DataFrame.")

    result = data.copy()
    prior = data[target].mean()

    for col in columns:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")
        if not pd.api.types.is_categorical_dtype(data[col]) and not pd.api.types.is_object_dtype(data[col]):
            warnings.warn(f"Column '{col}' is {data[col].dtype}, which is not categorical. Target encoding may not be appropriate.")

        averages = data.groupby(col)[target].agg(["count", "mean"])
        smoothing = 1 / (1 + np.exp(-(averages["count"] - min_samples_leaf) / smoothing))
        averages["smooth"] = prior * (1 - smoothing) + averages["mean"] * smoothing
        result[f"{col}_target_enc"] = data[col].map(averages["smooth"])

        if drop_original:
            result = result.drop(col, axis=1)

    return result

def correlation_feature_selection(data: pd.DataFrame, target: str, method: str = 'pearson', threshold: float = 0.5) -> pd.DataFrame:
    """
    Perform feature selection based on correlation analysis.

    Args:
        data (pd.DataFrame): The input DataFrame containing features and target.
        target (str): The name of the target column.
        method (str, optional): The correlation method to use. 
            Options: 'pearson', 'spearman', 'kendall'. Defaults to 'pearson'.
        threshold (float, optional): The correlation threshold for feature selection. 
            Features with absolute correlation greater than this value will be selected. 
            Defaults to 0.5.

    Returns:
        pd.DataFrame: DataFrame with selected features and their correlation with the target.
    """
    if target not in data.columns:
        raise ValueError(f"Target column '{target}' not found in the DataFrame.")

    # Separate features and target
    X = data.drop(columns=[target])
    y = data[target]

    # Calculate correlation
    if method == 'spearman':
        corr_matrix, _ = spearmanr(X, y)
        corr_with_target = pd.Series(corr_matrix[-1][:-1], index=X.columns)
    else:
        corr_with_target = X.apply(lambda x: x.corr(y, method=method))

    # Select features based on threshold
    selected_features = corr_with_target[abs(corr_with_target) > threshold]

    return pd.DataFrame({
        'feature': selected_features.index,
        'correlation': selected_features.values
    }).sort_values('correlation', key=abs, ascending=False)

def variance_feature_selection(self, data: pd.DataFrame, threshold: float = 0.0, columns: Union[str, List[str]] = None) -> pd.DataFrame:
    """
    Perform feature selection based on variance analysis.

    Args:
        data (pd.DataFrame): The input DataFrame containing features.
        threshold (float, optional): Features with a variance lower than this threshold will be removed. 
                                        Defaults to 0.0.
        columns (str or List[str], optional): Column label or sequence of labels to consider. 
                                                If None, use all columns. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with selected features and their variances.
    """
    if columns is None:
        columns = data.columns
    elif isinstance(columns, str):
        columns = [columns]

    # Select specified columns
    X = data[columns]

    # Initialize VarianceThreshold
    selector = VarianceThreshold(threshold=threshold)

    # Fit the selector
    selector.fit(X)

    # Get the mask of selected features
    feature_mask = selector.get_support()

    # Get the variances
    variances = selector.variances_

    # Create a DataFrame with selected features and their variances
    selected_features = pd.DataFrame({
        'feature': X.columns[feature_mask],
        'variance': variances[feature_mask]
    }).sort_values('variance', ascending=False)

    return selected_features

def scale_features(data: pd.DataFrame, 
                   columns: Union[str, List[str]], 
                   method: str = 'standard', 
                   copy: bool = True) -> pd.DataFrame:
    """
    Scale numerical features in the specified columns of a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or sequence of labels of numerical features to scale.
        method (str, optional): The scaling method to use. 
            Options: 'standard' for StandardScaler, 
                     'minmax' for MinMaxScaler, 
                     'robust' for RobustScaler. 
            Defaults to 'standard'.
        copy (bool, optional): If False, try to avoid a copy and do inplace scaling instead. 
            This is not guaranteed to always work inplace; e.g. if the data is not a NumPy array or scipy.sparse CSR matrix, 
            a copy may still be returned. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame with scaled features

    Raises:
        ValueError: If any of the specified columns are not numerical.
    """
    if isinstance(columns, str):
        columns = [columns]

    # Check if all specified columns are numerical
    non_numeric_cols = [col for col in columns if not pd.api.types.is_numeric_dtype(data[col])]
    if non_numeric_cols:
        raise ValueError(f"The following columns are not numerical: {non_numeric_cols}. "
                         "Please only specify numerical columns for scaling.")

    # Select the appropriate scaler
    if method == 'standard':
        scaler = StandardScaler(copy=copy)
    elif method == 'minmax':
        scaler = MinMaxScaler(copy=copy)
    elif method == 'robust':
        scaler = RobustScaler(copy=copy)
    else:
        raise ValueError("Invalid method. Choose 'standard', 'minmax', or 'robust'.")

    # Create a copy of the dataframe if required
    if copy:
        data = data.copy()

    # Fit and transform the selected columns
    scaled_data = scaler.fit_transform(data[columns])

    # Replace the original columns with scaled data
    data[columns] = scaled_data

    return data

def perform_pca(data: pd.DataFrame, n_components: Union[int, float, str] = 0.95, columns: Union[str, List[str]] = None, scale: bool = True) -> pd.DataFrame:
    """
    Perform Principal Component Analysis (PCA) on the specified columns of a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame.
        n_components (int, float, or str, optional): Number of components to keep.
            If int, it represents the exact number of components.
            If float between 0 and 1, it represents the proportion of variance to be retained.
            If 'mle', Minka's MLE is used to guess the dimension.
            Defaults to 0.95 (95% of variance).
        columns (str or List[str], optional): Column label or sequence of labels to consider.
            If None, use all columns. Defaults to None.
        scale (bool, optional): Whether to scale the data before applying PCA.
            Recommended when features are not on the same scale. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame with PCA results

    Example:
        >>> df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5], 'feature2': [2, 4, 5, 4, 5], 'feature3': [3, 6, 7, 8, 9]})
        >>> perform_pca(df, n_components=2)
                  PC1        PC2
        0  -2.121320  -0.707107
        1  -0.707107   0.707107
        2   0.000000   0.000000
        3   0.707107  -0.707107
        4   2.121320   0.707107
    """
    if columns is None:
        columns = data.columns
    elif isinstance(columns, str):
        columns = [columns]

    X = data[columns]

    # Check for non-numeric data types
    non_numeric_cols = X.select_dtypes(exclude=['number']).columns
    if not non_numeric_cols.empty:
        raise ValueError(f"Non-numeric data types detected in columns: {list(non_numeric_cols)}. "
                         "Please ensure all features are properly encoded and scaled before applying PCA.")

    # Warn if data doesn't seem to be scaled
    if (X.std() > 10).any():
        warnings.warn("Some features have high standard deviations. "
                      "Consider scaling your data before applying PCA for better results.")

    if scale:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(X)

    # Create a DataFrame with PCA results
    pca_df = pd.DataFrame(
        data=pca_result,
        columns=[f'PC{i+1}' for i in range(pca_result.shape[1])]
    )

    return pca_df

def perform_rfe(data: pd.DataFrame, 
                target: Union[str, pd.Series], 
                n_features_to_select: Union[int, float] = 0.5, 
                step: int = 1, 
                estimator: str = 'auto',
                columns: Union[str, List[str]] = None) -> pd.DataFrame:
    """
    Perform Recursive Feature Elimination (RFE) on the specified columns of a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame containing features.
        target (str or pd.Series): The target variable. If string, it should be the name of the target column in data.
        n_features_to_select (int or float, optional): Number of features to select.
            If int, it represents the exact number of features.
            If float between 0 and 1, it represents the proportion of features to select.
            Defaults to 0.5 (50% of features).
        step (int, optional): Number of features to remove at each iteration. Defaults to 1.
        estimator (str, optional): The estimator to use for feature importance ranking.
            Options: 'auto', 'logistic', 'rf', 'linear', 'rf_regressor'.
            'auto' will automatically choose based on the target variable type.
            Defaults to 'auto'.
        columns (str or List[str], optional): Column label or sequence of labels to consider.
            If None, use all columns except the target (if target is a column name in data).
            Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with selected features
    """
    # Prepare the feature matrix and target vector
    if isinstance(target, str):
        y = data[target]
        X = data.drop(columns=[target])
    else:
        y = target
        X = data

    # Select columns if specified
    if columns:
        if isinstance(columns, str):
            columns = [columns]
        X = X[columns]

    # Determine the number of features to select
    if isinstance(n_features_to_select, float):
        n_features_to_select = max(1, int(n_features_to_select * X.shape[1]))

    # Determine if the target is continuous or discrete
    is_continuous = np.issubdtype(y.dtype, np.number) and len(np.unique(y)) > 10

    # Choose the estimator
    if estimator == 'auto':
        estimator = 'linear' if is_continuous else 'logistic'

    if estimator == 'logistic':
        est = LogisticRegression(random_state=42)
    elif estimator == 'rf':
        est = RandomForestClassifier(random_state=42)
    elif estimator == 'linear':
        est = LinearRegression()
    elif estimator == 'rf_regressor':
        est = RandomForestRegressor(random_state=42)
    else:
        raise ValueError("Invalid estimator. Choose 'auto', 'logistic', 'rf', 'linear', or 'rf_regressor'.")

    # Perform RFE
    rfe = RFE(estimator=est, n_features_to_select=n_features_to_select, step=step)
    rfe.fit(X, y)

    # Get selected features
    selected_features = X.columns[rfe.support_].tolist()

    return data[selected_features]

def create_polynomial_features(data: pd.DataFrame, 
                               columns: Union[str, List[str]], 
                               degree: int = 2, 
                               interaction_only: bool = False, 
                               include_bias: bool = False) -> pd.DataFrame:
    """
    Create polynomial features from specified columns of a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or list of column labels to use for creating polynomial features.
        degree (int, optional): The degree of the polynomial features. Defaults to 2.
        interaction_only (bool, optional): If True, only interaction features are produced. Defaults to False.
        include_bias (bool, optional): If True, include a bias column (all 1s). Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with original and new polynomial features.

    Raises:
        ValueError: If specified columns are not numeric or if invalid parameters are provided.
    """
    if isinstance(columns, str):
        columns = [columns]

    # Check if specified columns exist and are numeric
    for col in columns:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")
        if not pd.api.types.is_numeric_dtype(data[col]):
            raise ValueError(f"Column '{col}' is {data[col].dtype}, which is not numeric. Polynomial features require numeric data.")

    if degree < 1:
        raise ValueError("Degree must be at least 1.")

    X = data[columns]
    poly = PolynomialFeatures(degree=degree, interaction_only=interaction_only, include_bias=include_bias)
    poly_features = poly.fit_transform(X)

    feature_names = poly.get_feature_names_out(columns)
    poly_df = pd.DataFrame(poly_features, columns=feature_names, index=data.index)

    # Remove duplicate columns (original features)
    poly_df = poly_df.loc[:, ~poly_df.columns.duplicated()]

    result = pd.concat([data, poly_df], axis=1)

    if result.shape[1] > 1000:
        warnings.warn("The resulting DataFrame has over 1000 columns. "
                      "This may lead to computational issues and overfitting.")

    return result

def create_feature_combinations(data: pd.DataFrame, 
                                columns: Union[str, List[str]], 
                                combination_type: str = 'multiplication', 
                                max_combination_size: int = 2) -> pd.DataFrame:
    """
    Create feature combinations from specified columns of a DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame.
        columns (str or List[str]): Column label or list of column labels to use for creating feature combinations.
        combination_type (str, optional): Type of combination to create. Options are 'multiplication' or 'addition'. Defaults to 'multiplication'.
        max_combination_size (int, optional): Maximum number of features to combine. Defaults to 2.

    Returns:
        pd.DataFrame: DataFrame with original and new combined features.

    Raises:
        ValueError: If specified columns are not numeric or if invalid parameters are provided.
    """
    if isinstance(columns, str):
        columns = [columns]

    # Check if specified columns exist and are numeric
    for col in columns:
        if col not in data.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")
        if not pd.api.types.is_numeric_dtype(data[col]):
            raise ValueError(f"Column '{col}' is {data[col].dtype} , which is not numeric. Feature combinations require numeric data.")

    if max_combination_size < 2:
        raise ValueError("max_combination_size must be at least 2.")

    if combination_type not in ['multiplication', 'addition']:
        raise ValueError("combination_type must be either 'multiplication' or 'addition'.")

    result = data.copy()

    for r in range(2, min(len(columns), max_combination_size) + 1):
        for combo in combinations(columns, r):
            if combination_type == 'multiplication':
                new_col = result[list(combo)].prod(axis=1)
                new_col_name = ' * '.join(combo)
            else:  # addition
                new_col = result[list(combo)].sum(axis=1)
                new_col_name = ' + '.join(combo)
            
            result[new_col_name] = new_col

    if result.shape[1] > 1000:
        warnings.warn("The resulting DataFrame has over 1000 columns. "
                      "This may lead to computational issues and overfitting.")

    return result

