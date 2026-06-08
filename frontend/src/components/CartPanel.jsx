export default function CartPanel({ cart, loading, error, onRemove }) {
  const items = cart?.items || [];

  return (
    <section className="cart-panel">
      <div className="cart-header">
        <h2>Shopping Cart</h2>
        <strong>€{formatMoney(cart?.total || 0)}</strong>
      </div>

      {loading && <p className="muted">Updating cart...</p>}
      {error && <p className="error-text">{error}</p>}

      {items.length === 0 ? (
        <p className="muted">Your cart is empty.</p>
      ) : (
        <div className="cart-items">
          {items.map((item) => (
            <div className="cart-item" key={item.product_id}>
              <div>
                <h3>{item.title}</h3>
                <p>
                  {item.quantity} x €{formatMoney(item.price)}
                </p>
                <strong>€{formatMoney(item.line_total)}</strong>
              </div>

              <button
                type="button"
                className="secondary-button"
                onClick={() => onRemove(item.product_id)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function formatMoney(value) {
  return Number(value).toFixed(2);
}
