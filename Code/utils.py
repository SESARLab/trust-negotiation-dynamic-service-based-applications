import typing

import pandas as pd


def compress_performance(input_file: str, performance_type: str, base_output_directory: str):
    if performance_type not in RESULT_TYPES:
        raise ValueError(f'performance_type must be one equal to {RESULT_TYPES}, got: {performance_type}')

    df = pd.read_csv(input_file)

    headers_to_group = [
        (['SERVICES', 'SERVICE_DATA'], f'performance_{performance_type}_service_first'),
        (['SERVICE_DATA', 'SERVICES'], f'performance_{performance_type}_servicedata_first')
    ]

    for header, base_name in headers_to_group:
        if performance_type == RESULT_TYPE_NEGOTIATION:
            columns_to_drop = ['MIN', 'MAX', 'STD']
        else:
            columns_to_drop = [col for col in df.columns if 'STD' in col or 'MAX' in col or 'MIN' in col]
        grouped = df.groupby(header).mean(numeric_only=True).drop(columns_to_drop, axis='columns')
        # let's move the multi-index to multiple column, so it is easier to plot.
        grouped = grouped.unstack(level=-1)
        # now, we have a multi-level column to be flattened. Let's do it.
        grouped.columns = grouped.columns.to_flat_index()
        # now, the name of the columns is like services, (avg, 10), (avg, 20), etc.
        # Let's "aggregate" the column names. Note that the first column is actually the index,
        # so we just have to wrap the tuple.
        grouped = grouped.rename(lambda col: f'{col[0]}_{col[1]}', axis='columns')
        grouped.to_csv(f'{base_output_directory}/{base_name}.csv', index=True)


def compress(input_files: typing.List[str], base_output_directory: str, prefix: str = '',
             columns_to_remove: typing.Optional[typing.List[str]] = None,
             drop_std: bool = False):
    # one DataFrame under the other
    df = pd.concat([pd.read_csv(f) for f in input_files])

    # let's first drop columns if necessary
    # If we are asked to remove STD-related columns, we add those columns to the list of columns to drop.
    if drop_std:
        to_drop = list(filter(lambda col: 'STD' in col, df.columns))
        columns_to_remove = to_drop if columns_to_remove is None else columns_to_remove + to_drop

    if columns_to_remove is not None and len(columns_to_remove) > 0:
        df = df.drop(columns_to_remove, axis='columns')

    # map between the headers to be used in group by and the name to use in output
    headers_to_group = [
        (['SERVICES', 'SERVICE_DATA'], f'{prefix}_service_first'),
        (['SERVICE_DATA', 'SERVICES'], f'{prefix}_servicedata_first')
    ]
    for header, base_name in headers_to_group:
        # compute the mean and retrieve avg only.
        grouped = df.groupby(header).mean(numeric_only=True)

        # let's move the multi-index to multiple column, so it is easier to plot.
        grouped = grouped.unstack(level=-1)
        # now, we have a multi-level column to be flattened. Let's do it.
        grouped.columns = grouped.columns.to_flat_index()
        # now, the name of the columns is like (col_name, 10), (col_name, 20), etc.,
        # where "col_name" is the col_name and 10 is the value we are grouping.
        # Let's join the column names from tuples to string.
        # Note that the first column is actually the index, so we just have to wrap the tuple.
        grouped = grouped.rename(lambda col: f'{col[0]}_{col[1]}', axis='columns')
        grouped.to_csv(f'{base_output_directory}/{base_name}.csv', index=True)


def group_func_group_change(setting: str) -> str:
    """

    Examples
    -------
    >>> setting_name = 'G2.3.3'
    >>> group_func_group_change(setting_name)
    ... 'G2.3.X'
    """
    parts = setting.split('.')
    if len(parts) != 3:
        raise ValueError(f'Split on {setting} failed, got {parts}')
    # join all parts but the last one.
    rejoined = '.'.join(parts[:-1])
    # and add 'X' add the end.
    return f'{rejoined}.X'


def group_func_group_basic(setting: str) -> str:
    """

    Examples
    -------
    >>> setting_name = 'G2.3.3'
    >>> group_func_group_basic(setting_name)
    ... 'GX.X.X'
    """
    parts = setting.split('.')
    if len(parts) != 3:
        raise ValueError(f'Split on {setting} failed, got {parts}')
    return f'GX.X.{parts[-1]}'


def average(input_file: str, grouping_func, output_file: str, drop_std: bool = False):
    # first we read the cvs file.
    df = pd.read_csv(input_file)
    # rename the first column which is unnamed because it is an index (when it has been exported)
    df = df.rename({'Unnamed: 0': 'Setting'}, axis='columns')
    # this seems very complicated, but actually we just change the value of the "Setting" column using group.
    df = df.apply(lambda row: pd.Series(
        [grouping_func(setting=row['Setting'])] + [row[k] for k in row.index if k != 'Setting'],
        index=row.index), axis='columns')
    # now, we just group and we are almost done.
    # NOTE: reset_index move the group-by index to the first column
    grouped = df.groupby('Setting').mean().reset_index()
    if drop_std:
        to_drop = list(filter(lambda col: 'STD' in col, df.columns))
        grouped = grouped.drop(to_drop, axis='columns')

    grouped.to_csv(output_file, index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()

    RESULT_TYPE_NEGOTIATION = 'negotiation'
    RESULT_TYPE_DYNAMIC = 'dynamic'
    RESULT_TYPES = [RESULT_TYPE_NEGOTIATION, RESULT_TYPE_DYNAMIC]

    parser_compress_performance = sub_parsers.add_parser('compress-performance')
    parser_compress_performance.add_argument('--base-output-directory', required=True, type=str)
    parser_compress_performance.add_argument('--input-file', required=True, type=str)
    parser_compress_performance.add_argument('--mode', choices=RESULT_TYPES, required=True, type=str)
    parser_compress_performance.set_defaults(func=lambda args_: compress_performance(
        input_file=args_.input_file,
        base_output_directory=args_.base_output_directory,
        performance_type=args_.mode
    ))

    parser_compress_quality = sub_parsers.add_parser('compress-quality')
    parser_compress_quality.add_argument('--base-output-directory', required=True, type=str)
    parser_compress_quality.add_argument('--input-files', required=True, nargs='*', type=str)
    parser_compress_quality.add_argument('--prefix', required=False, type=str)
    parser_compress_quality.add_argument('--columns-to-remove', nargs='*', required=False, type=str)
    parser_compress_quality.add_argument('--drop-std', required=False, type=bool)
    parser_compress_quality.set_defaults(func=lambda args_: compress(
        input_files=args_.input_files,
        prefix=args.prefix,
        columns_to_remove=args.columns_to_remove,
        drop_std=args.drop_std,
        base_output_directory=args_.base_output_directory,
    ))

    parser_compress_average = sub_parsers.add_parser('compress-average')
    parser_compress_average.add_argument('--input-file', required=True, type=str)
    parser_compress_average.add_argument('--output-file', required=True, type=str)
    parser_compress_average.add_argument('--drop-std', required=False, type=bool)
    parser_compress_average.add_argument('--mode', choices=RESULT_TYPES, required=True,
                                         type=str)
    parser_compress_average.set_defaults(func=lambda args_: average(
        input_file=args_.input_file,
        output_file=args_.output_file,
        drop_std=args.drop_std,
        grouping_func=group_func_group_change if args.mode == RESULT_TYPE_NEGOTIATION
        else group_func_group_basic
    ))

    args = parser.parse_args()
    args.func(args)
