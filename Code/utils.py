from pathlib import Path

import polars as pl


def aggregate_by_setting_level(
        input_file: Path,
        output_file: Path,
        output_cols: list[str],
        levels: list[int]) -> None:
    # read the input
    df = pl.read_csv(input_file)

    # "build the settings we're interested in.
    df = df.with_columns(
        extract_setting_level(
            pl.col("setting_name"), levels,
        ).alias("setting_group")
    )

    # build the result by doing the appropriate group by.
    result = (
        df
        .group_by("setting_group")
        .agg(
            *[
                pl.col(col).mean().alias(f"avg_{col}")
                for col in output_cols  # pick only the cols we're interested in.
            ],
            *[
                pl.col(col).std().alias(f"std_{col}")
                for col in output_cols
            ],
        )
        .sort("setting_group")
    )

    result.write_csv(output_file)


def pivot_on_metric(
        input_file: Path,
        output_file_pre: Path,
        target_col: str,
        filters: list[tuple[str, list[str]]] | None = None):
    df = pl.read_csv(input_file)
    # do the filter if any.
    if filters:
        for col, values in filters:
            df = df.filter(pl.col(col).is_in(values))

    groping_cols = ['n_services', 'n_trust_attributes']
    # we do a different pivot for each pair of headers.
    aggregated = df.group_by(groping_cols).agg(
        pl.col(target_col).mean().alias(f'avg_{target_col}'),
        pl.col(target_col).std().alias(f'std_{target_col}'),
    )

    # then, we do the pivot for 'n_services', first, and 'n_trust_attributes', second.
    # we need to do two pivots because pivoting works with one target col only. Then we unite.
    # The 'index' is what remains left, while the 'on' is the column that gets 'repeated'.
    pivoting_cols = [
        ['n_trust_attributes', 'n_services', 'ns'],
        ['n_services', 'n_trust_attributes', 'na'],
    ]
    for pivot_on, pivot_index, file_suffix in pivoting_cols:
        avg = pivot_and_rename(aggregated, pivot_index, pivot_on, target_col, col_prefix='avg')
        std = pivot_and_rename(aggregated, pivot_index, pivot_on, target_col, col_prefix='std')

        result = avg.join(std, on=pivot_index).sort(pivot_index)
        # now, just save.
        result.write_csv(output_file_pre.with_name(output_file_pre.name + f'_{file_suffix}.csv'))


def pivot_and_rename(df: pl.DataFrame, pivot_index: str, pivot_on: str, target_col: str,
                     col_prefix: str) -> pl.DataFrame:
    pivoted = df.pivot(on=pivot_on, index=pivot_index, values=f'{col_prefix}_{target_col}')
    # sort by columns.
    value_cols = sorted((c for c in pivoted.columns if c != pivot_index), key=int, )
    pivoted = pivoted.select([pivot_index, *value_cols])
    # then, we rename the columns using the format avg_{target_col}_{col}
    pivoted = pivoted.rename({c: f'{col_prefix}_{target_col}_{c}' for c in value_cols})
    return pivoted


def extract_setting_level(
        expr: pl.Expr,
        levels: list[int],
) -> pl.Expr:
    """
    Helper to extract a setting group from a setting column.

    The parameter tells which levels in the settings should be considered.

    Example assuming 'G1.1.1'.
    >>> extract_setting_level(pl.col('setting'), [0, 1])
    'G1.1.*'
    >>> extract_setting_level(pl.col('setting'), [2])
    'G*.*.1'
    >>> extract_setting_level(pl.col('setting'), [0, 2])
    'G1.*.1'
    """
    return (
        expr
        .str.split('.')
        .list.gather(levels)
        .list.join('.')
    )


import argparse


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True, )

    filter_pivot_parser = subparsers.add_parser('filter-pivot',
                                                help='Filter rows and generate a pivoted summary table.', )
    filter_pivot_parser.add_argument('--input-file', type=str, required=True)
    filter_pivot_parser.add_argument('--output-file', type=str, required=True)
    filter_pivot_parser.add_argument('--target-col', type=str, required=True,
                                     help='Target column name.')
    filter_pivot_parser.add_argument('--filter', action='append', default=[],
                                     help='Filter on columns of the form col-name=<val1><valn>. Vals are in OR.')
    filter_pivot_parser.set_defaults(func=cmd_pivot_on_metric)

    aggregate_parser = subparsers.add_parser("aggregate-setting-level",
                                             help="Aggregate metrics on selected setting levels.",
                                             )
    aggregate_parser.add_argument("--input-file", type=str, required=True, )
    aggregate_parser.add_argument("--output-file", type=str, required=True, )
    aggregate_parser.add_argument("--output-cols", nargs="+", required=True, )
    aggregate_parser.add_argument("--levels", nargs="+", required=True, )
    aggregate_parser.set_defaults(func=cmd_aggregate_by_setting_level, )

    args = parser.parse_args()
    args.func(args)


def cmd_pivot_on_metric(args) -> None:
    filters = None

    if args.filter:
        filters = []
        for f in args.filter:
            col, values = f.split('=', 1)
            filters.append((col, values.split(',')))

    pivot_on_metric(
        input_file=Path(args.input_file),
        output_file_pre=Path(args.output_file),
        target_col=args.target_col,
        filters=filters,
    )


def cmd_aggregate_by_setting_level(args) -> None:
    aggregate_by_setting_level(
        input_file=Path(args.input_file),
        output_file=Path(args.output_file),
        output_cols=args.output_cols,
        levels=[int(x) for x in args.levels],
    )


if __name__ == '__main__':
    main()
