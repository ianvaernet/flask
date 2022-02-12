class MutationException(Exception):
    def __init__(
        self,
        mutation,
        descriptions,
        title="Mutation Error",
    ):
        super().__init__()
        self.mutation
        self.description
