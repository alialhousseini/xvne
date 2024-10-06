'''A class for computing and evaluate the performance of the VNE'''
from Networks import VirtualNetworkRequest, SubstrateNetwork
import json


class Evaluator:
    def __init__(self, vnrs: list[VirtualNetworkRequest], sn: SubstrateNetwork) -> None:
        self.trial_count: int = 0
        self.vnrs = vnrs
        self.sn = sn
        self.num_vnrs: int = len(vnrs)
        self.vnrs_embedded: int = 0  # the number of embedded VNRs
        self.processed_vnrs: int = 0  # the number of processed VNRs
        # the list of ids of embedded VNRs (used to retrieve resources/cost)
        self.vnrs_embedded_list: list[int] = []
        # Record AR within several experiments
        self.acceptance_ratios: list[float] = []
        # Record RE within several experiments
        self.resource_efficiencies: list[float] = []
        self.beta: int = 1  # TODO: v2.0 - beta is inspired from SN design

    def add_embedded_vnr(self, vnr: VirtualNetworkRequest) -> None:
        self.vnrs_embedded_list.append(vnr.id)
        self.vnrs_embedded += 1

    def get_embedded_vnr(self, vnr_id: int) -> VirtualNetworkRequest:
        for vnr in self.vnrs:
            if vnr.id == vnr_id:
                return vnr

    def evaluate(self) -> None:
        '''This function will compute created metrics within an experiment
           To get complete results, use to_json()    
        '''
        acc_ratio: float = self.vnrs_embedded / self.num_vnrs
        revenue = self.compute_revenue()
        cost = self.compute_cost()
        re = revenue/cost

        self.acceptance_ratios.append(acc_ratio)
        self.resource_efficiencies.append(re)

    def compute_revenue(self) -> float:
        caps = 0
        bws = 0
        for id in self.vnrs_embedded_list:
            vnr = self.get_embedded_vnr(id)
            temp_caps = sum(
                list(map(lambda node: node.capacity, vnr.virtual_network.virtual_nodes)))
            temp_bws = sum(list(map(lambda link: link.bandwidth,
                           vnr.virtual_network.virtual_links)))
            caps += temp_caps
            bws += temp_bws
        return caps + self.beta * bws

    def compute_cost(self) -> float:
        caps = 0
        bws = 0
        for id in self.vnrs_embedded_list:
            vnr = self.get_embedded_vnr(id)
            temp_caps = sum(
                list(map(lambda node: node.capacity, vnr.virtual_network.virtual_nodes)))
            temp_bws = sum(list(map(lambda link: link.bandwidth * len(link.substrate_path),
                           vnr.virtual_network.virtual_links)))
            caps += temp_caps
            bws += temp_bws
        return caps + self.beta * bws

    def to_json(self, filename: str) -> None:
        '''Saves a json file with all info required'''
        info = {
            "vnrs_embedded": self.vnrs_embedded,
            "avg_acceptance_ratios": sum(self.acceptance_ratios)/len(self.acceptance_ratios),
            "resource_efficiencies": sum(self.resource_efficiencies)/len(self.resource_efficiencies),
            "beta": self.beta,
        }

        with open(filename, 'w') as json_file:
            json.dump(info, json_file, indent=4)

        print(f"Evaluation results saved to {filename}")

    def is_all_vnrs_embedded(self) -> bool:
        return self.vnrs_embedded == self.num_vnrs

    def is_all_vnrs_processed(self) -> bool:
        return self.processed_vnrs == self.num_vnrs
