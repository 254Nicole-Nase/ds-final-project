import os
import aiohttp
import asyncio
import matplotlib.pyplot as plt

RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def send_requests(num_requests, base_url="http://localhost:5000/home"):
    server_counts = {}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, base_url) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)
        for res in responses:
            print("DEBUG:", res)  # Add this line to see what you get
            if not isinstance(res, dict):
                print("Unexpected response (not dict):", res)
                continue
            if res.get("status") == "successful":
                server_id = res["message"].split(": ")[1]
                server_counts[server_id] = server_counts.get(server_id, 0) + 1
    return server_counts

async def get_replica_status(session, url="http://localhost:5000/rep"):
    try:
        async with session.get(url) as response:
            return await response.json()
    except Exception as e:
        print(f"Error fetching replica status: {e}")
        return None

async def add_replicas(session, n, url="http://localhost:5000/add"):
    payload = {"n": n}
    async with session.post(url, json=payload) as response:
        return await response.json()

async def remove_replicas(session, n, url="http://localhost:5000/rm"):
    payload = {"n": n}
    async with session.delete(url, json=payload) as response:
        return await response.json()

def plot_bar_chart(data, title, xlabel, ylabel):
    servers = list(data.keys())
    counts = list(data.values())
    plt.figure(figsize=(10, 6))
    plt.bar(servers, counts, color='skyblue')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(os.path.join(RESULTS_DIR, f"{title.replace(' ', '_')}.png"))
    plt.close()

def plot_line_chart(x_values, y_values, title, xlabel, ylabel):
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.savefig(os.path.join(RESULTS_DIR, f"{title.replace(' ', '_')}.png"))
    plt.close()

async def main():
    print("Starting analysis...")
    async with aiohttp.ClientSession() as session:
        # A-1: Load distribution for N=3
        print("\n--- Running A-1: Load distribution for N=3 ---")
        server_replica_info = await get_replica_status(session)
        if server_replica_info and server_replica_info["status"] == "successful":
            initial_servers_N = server_replica_info["message"]["N"]
            if initial_servers_N < 3:
                await add_replicas(session, 3 - initial_servers_N)
            elif initial_servers_N > 3:
                await remove_replicas(session, initial_servers_N - 3)
        server_counts_a1 = await send_requests(10000)
        print(f"A-1 Server Request Counts: {server_counts_a1}")
        plot_bar_chart(server_counts_a1, "A-1: Request Distribution (N=3)", "Server ID", "Request Count")

        # A-2: Scalability from N=2 to N=6
        print("\n--- Running A-2: Scalability (N=2 to N=6) ---")
        avg_loads = []
        N_values = range(2, 7)
        for N in N_values:
            print(f"Testing with N={N} servers...")
            replica_info = await get_replica_status(session)
            current_N = replica_info["message"]["N"]
            if current_N < N:
                await add_replicas(session, N - current_N)
            elif current_N > N:
                await remove_replicas(session, current_N - N)
            server_counts_a2 = await send_requests(10000)
            total_requests = sum(server_counts_a2.values())
            avg_load = total_requests / N if N > 0 else 0
            avg_loads.append(avg_load)
            print(f"N={N}, Avg Load: {avg_load}, Counts: {server_counts_a2}")
        plot_line_chart(N_values, avg_loads, "A-2: Average Load vs. Number of Servers", "Number of Servers (N)", "Average Requests per Server")

        # A-3: Server Failure Recovery
        print("\n--- Running A-3: Server Failure Recovery ---")
        await add_replicas(session, 3)
        initial_replicas_info = await get_replica_status(session)
        initial_replicas = initial_replicas_info["message"]["replicas"]
        if initial_replicas:
            server_to_stop = initial_replicas[0]
            print(f"Manually stop one server, e.g., run `docker stop {server_to_stop}` in your terminal.")
            print("Then press Enter to continue...")
            input()
            print("Sending requests to trigger fault detection...")
            server_counts_after_failure = await send_requests(50)
            print(f"Server counts after failure (expecting new server): {server_counts_after_failure}")
            final_replicas_info = await get_replica_status(session)
            print(f"Replicas after failure attempt: {final_replicas_info}")

        print("\n--- A-4: Impact of Modified Hash Functions ---")
        print("Change hash functions in balancer/hashing.py, rebuild, and re-run this script for A-4.")

if __name__ == "__main__":
    asyncio.run(main())