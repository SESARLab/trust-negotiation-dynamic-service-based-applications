python experiments.py --output-dir $BASE_OUTPUT_DIR

mkdir $BASE_OUTPUT_DIR/post

# quality negotiation for the worst case of G2.3.X.
python utils.py \
    compress-quality \
    --base-output-directory $BASE_OUTPUT_DIR/post \
    --input-files $BASE_OUTPUT_DIR/quality/raw_results/negotiation/raw_results_G2.3.1.csv \
   $BASE_OUTPUT_DIR/quality/raw_results/negotiation/raw_results_G2.3.2.csv \
    $BASE_OUTPUT_DIR//quality/raw_results/negotiation/raw_results_G2.3.3.csv \
    --prefix quality_negotiation_G2.3.X_ \
    --drop-std true

# quality dynamic trust for the worst case of GX.X.3.
python utils.py \
    compress-quality \
    --base-output-directory $BASE_OUTPUT_DIR/post \
    --input-files \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G1.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G1.3.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G2.1.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G2.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G2.3.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G3.1.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G3.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G3.3.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G4.1.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G4.2.3.csv \
    $BASE_OUTPUT_DIR/quality/raw_results/dynamic_trust/raw_results_G4.3.3.csv \
    --prefix quality_dynamic_GX.X.3_ \
    --drop-std true


# performance dynamic trust
python utils.py compress-performance \
	--mode dynamic \
	--base-output-directory $BASE_OUTPUT_DIR/post \
	--input-file $BASE_OUTPUT_DIR/performance/dynamic_trust/results.csv
		
# performance negotiation
python utils.py compress-performance \
    --mode negotiation \
    --base-output-directory $BASE_OUTPUT_DIR/post \
    --input-file $BASE_OUTPUT_DIR/performance/negotiation/results.csv

# compress negotiation (for tables)
python utils.py \
    compress-average \
    --input-file $BASE_OUTPUT_DIR/quality/elaborated_results/negotiation_results.csv \
    --output-file $BASE_OUTPUT_DIR/post/negotiation_results.csv \
    --mode negotiation \
    --drop-std true

# compress dynamic trust (for tables)
python utils.py \
    compress-average \
    --input-file $BASE_OUTPUT_DIR/quality/elaborated_results/dynamic_trust_results.csv \
    --output-file $BASE_OUTPUT_DIR/post/dynamic_trust_results.csv \
    --mode dynamic \
    --drop-std true
