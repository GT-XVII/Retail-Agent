export default function ProductCard({ product }) {
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
        {product.inventory > 0 ? `${product.inventory} in stock` : "Out of stock"}
      </p>

      <p className="features">{product.features}</p>
    </div>
  );
}