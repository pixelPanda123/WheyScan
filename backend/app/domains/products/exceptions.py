class ProductDomainError(Exception):
    pass


class ProductNotFoundError(ProductDomainError):
    pass


class ProductAlreadyExistsError(ProductDomainError):
    pass


class ProductBrandNotFoundError(ProductDomainError):
    pass
