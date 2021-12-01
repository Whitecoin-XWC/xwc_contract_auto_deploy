import os.path
import subprocess
import time
import json
import requests
import argparse

UVM_EXE = "uvm_ass.exe"
PACKAGE_EXE = "package_gpc.exe"
XWC_RPC_ADDR = "127.0.0.1:29000"


def rpc_request(url, method, args):
    args_j = json.dumps(args)
    payload = "{\r\n \"id\": 1,\r\n \"method\": \"%s\",\r\n \"params\": %s\r\n}" % (method, args_j)
    headers = {
        'content-type': "text/plain",
        'cache-control': "no-cache",
    }
    # logging.debug(self.baseUrl)
    for i in range(5):
        try:
            print("[HTTP POST] %s" % payload)
            response = requests.request("POST", f"http://{url}", data=payload, headers=headers)
            rep = response.json()
            if response.status_code != 200:
                print("response code error", response.status_code)
                continue
            return json.loads(response.text)

        except Exception as ex:
            print(f"Retry: {payload}")
            time.sleep(5)
            continue
    return None


class XwcContractLoader:
    def __init__(self, ass_path, meta_path):

        if not os.path.exists(ass_path):
            raise SystemExit(f"{ass_path} can not be found!")

        if not os.path.exists(meta_path):
            raise SystemExit(f"{meta_path} can not be found!")

        self.ass_file = ass_path
        self.meta_file = meta_path
        self.contract_id = None

        # file_name = Path(ass_path).name.split('.')[0]
        file_name = os.path.basename(self.ass_file).split(".")[0]

        self.out_file = file_name + ".out"
        self.gpc_file = file_name + ".gpc"

        # clean the output files
        if os.path.exists(self.out_file):
            os.remove(self.out_file)
        if os.path.exists(self.gpc_file):
            os.remove(self.gpc_file)

    def __compile_ass(self):
        """
        calling uvm_ass.exe to generate result.out
        :return:
        """
        _cmd = f"{UVM_EXE} {self.ass_file}"
        print(f"Running command '{_cmd}'")
        subprocess.run(_cmd,
                       shell=True,
                       stdout=subprocess.PIPE)

        if os.path.exists(self.out_file):
            print(f"Successfully generating {self.out_file}")
        else:
            raise SystemExit(f"failed to generate {self.out_file}")

    def __compile_package(self):
        """
        calling package_gpc.exe to generate result.gpc
        :return:
        """
        _cmd = f"{PACKAGE_EXE} {self.out_file} {self.meta_file}"
        print(f"Running command '{_cmd}'")
        subprocess.run(_cmd,
                       shell=True,
                       stdout=subprocess.PIPE)

        if os.path.exists(self.gpc_file):
            print(f"Successfully generating {self.gpc_file}")

        else:
            raise SystemExit(f"failed to generate {self.gpc_file}")

    def generate_gpc(self):
        self.__compile_ass()
        self.__compile_package()

    def deploy(self, rpc_addr, xwc_user):
        """
        deploy smart contract by RPC call
        :return:
        """
        # res = rpc_request(rpc_addr, "register_contract", [xwc_user, "0.0001", "500000", self.gpc_file])

        res = rpc_request(rpc_addr, "register_contract",
                          [xwc_user, "0.0001", "500000", f"{os.path.abspath('.')}/{self.gpc_file}"])
        if res is None:
            raise SystemExit(
                f"Failed to connect XWC environment via RPC call! Please check if XWC testing environment runs well!")

        _err = res.get('error')
        if _err is not None:
            raise SystemExit(
                f"Failed to deploy contract! {_err.get('message')}")

        self.contract_id = res.get('result').get('contract_id')
        if self.contract_id is None:
            print(f"Failed to deploy {self.gpc_file} to the local XWC environment:")
            print(res)
            raise SystemExit(f"Failed to deploy {self.gpc_file} to the local XWC environment!")

        print(f"Successfully deployed the smart contract!")
        print(f"The contract ID is: '{self.contract_id}'")

    def run_testcase(self):
        """
        here we can run some testcases to check if the contract works as expected.
        Or we can make another isolate test framework to do so!
        :return:
        """
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This program helps generate the .gpc file and deploy it to the "
                                                 "XWC blockchain")

    parser.add_argument('ass_file_path', help='The input .ass file')
    parser.add_argument('meta_file_path', help='The input .meta.json file')
    parser.add_argument('--xwc_user', default="xwc", required=False, help='The XWC user used for deploying the contract')
    parser.add_argument('--nodeploy', action="store_true", help='generate .gpc file only, do not deploy.')

    args = parser.parse_args()

    xwcContract = XwcContractLoader(args.ass_file_path, args.meta_file_path)

    print("Start encoding the XWC smart contract!")
    xwcContract.generate_gpc()

    if args.nodeploy:
        print("Ignore deploying with flag '--nodeploy'...")
    else:
        print("Start deploying the XWC smart contract")
        xwcContract.deploy(XWC_RPC_ADDR, args.xwc_user)

    print("Finished!")
