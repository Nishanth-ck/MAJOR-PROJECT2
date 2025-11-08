from state import load_state, save_state

state = load_state()
state["startMonitoring"] = True   # enable monitoring
save_state(state)

print("✅ Monitoring enabled! Now run file_protector2.py")


