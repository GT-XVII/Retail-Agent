import { useEffect, useState } from "react";
import { fetchProducts } from "./api";
import ChatPanel from "./components/ChatPanel";
import ProductGrid from "./components/ProductGrid";
import "./index.css";

export default function App() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState([]);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(true);

  async function loadProducts(searchQuery = query) {
    setLoading(true);

    try {
      const data = await fetchProducts(searchQuery, limit);
      setProducts(data.products || data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    fetchProducts("", limit)
      .then((data) => {
        if (!cancelled) {
          setProducts(data.products || data);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [limit]);

  function handleSearch(event) {
    event.preventDefault();
    loadProducts(query);
  }

  return (
    <main className="app">
      <header>
        <h1>Retail Agent</h1>
        <p>Demo electronics store with catalogue search and AI chat.</p>
      </header>

      <div className="layout">
        <section className="store">
          <div className="store-header">
            <h2>Demo Store</h2>

            <form onSubmit={handleSearch}>
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search keyboards, monitors, headphones..."
              />

              <select
                value={limit}
                onChange={(event) => {
                  setLoading(true);
                  setLimit(Number(event.target.value));
                }}
              >
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>

              <button type="submit">Search</button>
            </form>
          </div>

          {loading ? <p>Loading products...</p> : <ProductGrid products={products} />}
        </section>

        <ChatPanel />
      </div>
    </main>
  );
}
