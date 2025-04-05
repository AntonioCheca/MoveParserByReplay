import cProfile
import pstats


class ProfilerWrapper:
    profiler: cProfile.Profile

    def __init__(self):
        self.profiler = cProfile.Profile()

    def enable(self) -> None:
        self.profiler.enable()

    def disable(self) -> None:
        self.profiler.disable()

    def print_results(self) -> None:
        stats = pstats.Stats(self.profiler).sort_stats('tottime')
        stats.print_stats(20)

    def dump_in_profiler_file_for_details(self) -> None:
        self.profiler.dump_stats("profile_output.prof")
