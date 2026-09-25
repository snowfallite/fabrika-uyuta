from hypothesis import settings

settings.register_profile("ci", max_examples=200, deadline=None, derandomize=True)
settings.register_profile("dev", max_examples=50, deadline=None)
settings.load_profile("dev")
