
def evaluate_fingerprint(**fp_kwargs):
    from spec_builder import main_fn
        
    tenant_id = fp_kwargs['current_tenant']    
    main_fn.main(tenant_id)