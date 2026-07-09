class ListingsDomainError(Exception):
    pass


class StoreNotFoundError(ListingsDomainError):
    pass


class StoreAlreadyExistsError(ListingsDomainError):
    pass


class StoreHasListingsError(ListingsDomainError):
    pass


class ListingNotFoundError(ListingsDomainError):
    pass


class ListingAlreadyExistsError(ListingsDomainError):
    pass


class ListingProductNotFoundError(ListingsDomainError):
    pass


class ListingStoreNotFoundError(ListingsDomainError):
    pass
