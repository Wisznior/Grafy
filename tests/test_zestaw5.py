from pathlib import Path

import pytest

from grafy.zestaw5.flow_network import FlowNetwork, random_flow_network, draw_flow_network
from grafy.zestaw5.max_flow import ford_fulkerson


@pytest.mark.parametrize("layers", [2, 3, 4])
def test_random_network_obeys_layer_and_capacity_rules(layers):
    network = random_flow_network(layers, seed=layers)
    assert len(network.layers) == layers + 2
    assert all(2 <= len(layer) <= layers for layer in network.layers[1:-1])
    assert all(1 <= capacity <= 10 for capacity in network.capacities.values())
    for current, following in zip(network.layers, network.layers[1:]):
        assert all(any(u == source and v in following for u, v in network.capacities)
                   for source in current)
        assert all(any(v == target and u in current for u, v in network.capacities)
                   for target in following)
    assert not any(v == network.source or u == network.sink for u, v in network.capacities)


def test_edmonds_karp_uses_reverse_residual_arc_to_reroute():
    capacities = {
        (0, 1): 1, (0, 2): 1, (1, 3): 1, (1, 4): 1,
        (2, 3): 1, (3, 5): 1, (4, 5): 1,
    }
    network = FlowNetwork([[0], [1, 2], [3, 4], [5]], capacities)
    result = ford_fulkerson(network)
    assert result.value == 2
    assert any(amount == 1 and path == [0, 2, 3, 1, 4, 5]
               for path, amount in result.augmentations)
    assert all(0 <= result.flows[arc] <= cap for arc, cap in capacities.items())
    for vertex in [1, 2, 3, 4]:
        inflow = sum(flow for (u, v), flow in result.flows.items() if v == vertex)
        outflow = sum(flow for (u, v), flow in result.flows.items() if u == vertex)
        assert inflow == outflow


def test_flow_network_draws_flow_over_capacity(tmp_path):
    network = random_flow_network(2, seed=9)
    result = ford_fulkerson(network)
    image = tmp_path / "flow.png"
    draw_flow_network(network, image, result.flows)
    assert image.stat().st_size > 0


def test_generator_rejects_less_than_two_layers():
    with pytest.raises(ValueError):
        random_flow_network(1)
