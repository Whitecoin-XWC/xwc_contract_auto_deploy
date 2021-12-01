# xwc_contract_auto_deploy

This python script helps generate .gpc file from .ass file and deploy it to a certain XWC environment. This can be used in a XWC smart contract developing/testing environment.

1. Before running this auto-deploy script, make sure you have compiled the contract successfully and got the output files: result.ass and result.meta.json.
2. Make sure the XWC testing environment is running.  
3. Setup the "XWC_RPC_ADDR" to the XWC testing environment you want to use. For the local XWC testing environment running by start_xwc_local.py(https://github.com/Whitecoin-XWC/xwc_chain_local_testing_environment), the default value is no need to be changed.
4. Running command to deploy the contract:
```shell
python xwc_deploy_contract.py <ass_file> <meta_file>
```

  The contract ID will be returned in the output if everything works well.
  
  You can just generate .gpc only and don't make the deployment with the flag '--nodeploy':
  ```shell
  python xwc_deploy_contract.py <ass_file> <meta_file> --nodeploy
  ```
