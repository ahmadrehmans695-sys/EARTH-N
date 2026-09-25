import networkx as nx
import pandas as pd


def create_earth_network():
    """
    Create the Earth-N interconnected infrastructure network.

    Each node contains:
    - sector
    - importance
    - capacity
    - demand
    - operational state
    - service level

    Each connection contains:
    - dependency strength
    - capacity
    """

    G = nx.DiGraph()

    nodes = [
        # Electricity
        ("PowerPlant", "electricity", 100, 100, 70),
        ("GridStation", "electricity", 90, 100, 80),
        ("Substation_A", "electricity", 70, 100, 75),
        ("Substation_B", "electricity", 70, 100, 75),

        # Water
        ("WaterPlant", "water", 80, 100, 70),
        ("WaterPump_A", "water", 80, 80, 60),
        ("WaterPump_B", "water", 80, 80, 60),

        # Telecommunications
        ("Telecom_Tower_A", "telecom", 50, 80, 50),
        ("Telecom_Tower_B", "telecom", 50, 80, 50),

        # Transport
        ("Road_A", "transport", 50, 100, 60),
        ("Road_B", "transport", 50, 100, 60),

        # Critical facilities
        ("Hospital", "critical", 100, 100, 80),
        ("Emergency_Center", "critical", 90, 100, 70),
        ("Industrial_Plant", "critical", 80, 100, 85),
    ]

    for name, sector, importance, capacity, demand in nodes:
        G.add_node(
            name,
            sector=sector,
            importance=importance,
            capacity=capacity,
            demand=demand,
            operational=True,
            service_level=1.0,
        )

    # -------------------------------------------------
    # INFRASTRUCTURE DEPENDENCIES
    #
    # dependency_strength:
    # 1.0 = essential
    # 0.5 = moderate
    # 0.2 = weak
    # -------------------------------------------------

    connections = [
        # Electricity network
        ("PowerPlant", "GridStation", 1.0),
        ("GridStation", "Substation_A", 1.0),
        ("GridStation", "Substation_B", 1.0),

        # Electricity dependencies
        ("Substation_A", "Hospital", 1.0),
        ("Substation_A", "WaterPump_A", 1.0),
        ("Substation_A", "Telecom_Tower_A", 1.0),

        ("Substation_B", "Emergency_Center", 1.0),
        ("Substation_B", "WaterPump_B", 1.0),
        ("Substation_B", "Telecom_Tower_B", 1.0),
        ("Substation_B", "Industrial_Plant", 1.0),

        # Water dependencies
        ("WaterPlant", "WaterPump_A", 1.0),
        ("WaterPlant", "WaterPump_B", 1.0),

        ("WaterPump_A", "Hospital", 0.8),
        ("WaterPump_B", "Industrial_Plant", 0.7),

        # Telecom dependencies
        ("Telecom_Tower_A", "Emergency_Center", 0.2),
        ("Telecom_Tower_B", "Hospital", 0.2),

        # Transport dependencies
        ("Road_A", "Hospital", 0.1),
        ("Road_B", "Emergency_Center", 0.1),
        ("Road_B", "Industrial_Plant", 0.1),
    ]

    for source, target, dependency_strength in connections:
        G.add_edge(
            source,
            target,
            operational=True,
            capacity=100,
            dependency_strength=dependency_strength,
        )

    return G


def network_summary(G):
    """Return infrastructure status as a DataFrame."""

    data = []

    for node, attributes in G.nodes(data=True):
        data.append(
            {
                "Node": node,
                "Sector": attributes["sector"],
                "Importance": attributes["importance"],
                "Capacity": attributes["capacity"],
                "Demand": attributes["demand"],
                "Operational": attributes["operational"],
                "Service_Level": attributes["service_level"],
            }
        )

    return pd.DataFrame(data)


if __name__ == "__main__":
    network = create_earth_network()

    print("=" * 70)
    print("EARTH-N — DEPENDENCY-AWARE INFRASTRUCTURE MODEL")
    print("=" * 70)

    print(f"Total infrastructure nodes: {network.number_of_nodes()}")
    print(f"Total infrastructure connections: {network.number_of_edges()}")

    print("\nINFRASTRUCTURE STATUS")
    print("-" * 70)

    print(network_summary(network).to_string(index=False))

    print("\nDEPENDENCY CONNECTIONS")
    print("-" * 70)

    for source, target, data in network.edges(data=True):
        print(
            f"{source:20} -> "
            f"{target:20} | "
            f"Dependency: {data['dependency_strength']:.1f}"
        )

    print("\nEARTH-N DEPENDENCY MODEL CREATED SUCCESSFULLY")