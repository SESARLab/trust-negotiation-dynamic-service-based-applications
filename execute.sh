python main.py --output-dir $DEST_DIR

# walkthrough.
python walkthrough.py > $DEST_DIR/walkthrough.json5

# post-processing
mkdir $DEST_DIR/03_post

# negotiation - success rate over settings G2.3.*
python utils.py filter-pivot \
  --input-file $DEST_DIR/01_quality/02_agg1_results.csv \
  --output-file $DEST_DIR/03_post/sensitivity_G2.3.X \
  --filter setting_name=G2.3.1,G2.3.2,G2.3.3 \
  --target-col avg_negotiation_success_rate


# negotiation - success rate, success rate SOTA
# note that for SOTA1 and 3 we export just one
# metrics 'cause everything is 0 and that's it.
python utils.py aggregate-setting-level \
  --input-file $DEST_DIR/01_quality/01_agg2_results.csv \
  --output-file $DEST_DIR/03_post/quality_neg_comparison.csv \
  --levels 0 1 \
  --output-cols \
    avg_avg_negotiation_success_rate \
    avg_avg_trust_value \
    avg_avg_sota1_success_rate \
    avg_avg_sota2_success_rate \
    avg_avg_sota2_trust_value \
    avg_avg_sota2_unsupported_service_rate \
    avg_avg_sota2_requirement_violation_rate \
    avg_avg_sota3_success_rate


# dynamic trust - quality
python utils2.py aggregate-setting-level \
  --input-file $DEST_DIR/01_quality/01_agg2_results.csv \
  --output-file $DEST_DIR/03_post/quality_dyn_comparison.csv \
  --levels 2 \
  --output-cols \
    avg_avg_global_application_stability \
    avg_avg_global_service_stability


# performance - negotiation
python utils2.py filter-pivot \
  --input-file $DEST_DIR/02_performance/performance.csv \
  --output-file $DEST_DIR/03_post/performance_01neg_G2.3.X_G.4.2.X \
  --filter setting_name=G2.3.1,G2.3.2,G2.3.3,G4.2.1,G4.2.2,G4.2.3 \
  --target-col negotiation_avg

# performance - dynamic trust
python utils2.py filter-pivot \
  --input-file $DEST_DIR/02_performance/performance.csv \
  --output-file $DEST_DIR/03_post/performance_02dyn_G2.3.X_G.4.2.X \
  --filter setting_name=G2.3.1,G2.3.2,G2.3.3,G4.2.1,G4.2.2,G4.2.3 \
  --target-col dynamic_trust_avg

