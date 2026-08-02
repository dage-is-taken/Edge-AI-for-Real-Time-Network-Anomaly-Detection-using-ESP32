import numpy as np


def create_windows(X, y=None, window_size=10):
    """
    Convert sequential samples into overlapping windows.

    Parameters
    ----------
    X : pandas.DataFrame or numpy.ndarray
        Feature matrix.

    y : pandas.Series or numpy.ndarray, optional
        Labels.

    window_size : int
        Number of consecutive samples per window.

    Returns
    -------
    X_windows : numpy.ndarray

    y_windows : numpy.ndarray (if labels provided)
    """

    X = np.asarray(X)

    X_windows = []

    y_windows = []

    for i in range(len(X) - window_size + 1):

        X_windows.append(
            X[i:i + window_size]
        )

        if y is not None:

            y_windows.append(
                y.iloc[i + window_size - 1]
                if hasattr(y, "iloc")
                else y[i + window_size - 1]
            )

    X_windows = np.array(X_windows)

    if y is None:
        return X_windows

    y_windows = np.array(y_windows)

    print("=" * 60)
    print("Window Creation")
    print("=" * 60)

    print(f"Window Size : {window_size}")
    print(f"Input Samples : {len(X)}")
    print(f"Output Windows : {len(X_windows)}")
    print(f"Window Shape : {X_windows.shape}")

    return X_windows, y_windows