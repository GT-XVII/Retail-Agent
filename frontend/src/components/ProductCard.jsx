export default function ProductCard({ product, onAddToCart }) {
  const inStock = product.inventory > 0;

  return (
    <div className="product-card">
      {product.image_url && (
        <img src={product.image_url} alt={product.title} />
      )}

      <h3>{product.title}</h3>

      <p className="brand">{product.brand || "Unknown brand"}</p>

      <p className="price">€{product.price}</p>

      <p className="rating">
        {product.average_rating} stars ({product.rating_number} ratings)
      </p>

      <p className="stock">
        {inStock ? `${product.inventory} in stock` : "Out of stock"}
      </p>

      <p className="features">{product.features}</p>

      <button
        type="button"
        className="add-cart-button"
        disabled={!inStock}
        onClick={() => onAddToCart(product.id)}
      >
        Add to cart
      </button>
    </div>
  );
}
