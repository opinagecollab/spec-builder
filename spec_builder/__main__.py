import builderfingerprint as bf
from spec_builder.services import fingerprint_service as fp_srv

# Set Builder ID
bf.set_builder('spec-builder','Builds specs for a product')

# Set Builder table
bf.set_builder_table('spec_builder_job')

# Set Evaluate function
bf.set_evaluate_fn(fp_srv.evaluate_fingerprint)

# Set Frequency
bf.set_scheduler_interval(86400)

# Set Builder Frequency
bf.set_builder_frequency(86400)

# Initialise the fingerprinting mechanism
bf.init()