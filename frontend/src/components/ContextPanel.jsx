// frontend/src/components/ContextPanel.jsx

function ContextPanel({ citations }) {
  return (
    <aside className="context-panel">
      <h3>מקורות מהחומר שלך</h3>

      {!citations || citations.length === 0 ? (
        <p className="context-empty">
          אחרי שתשאל שאלה על חומר הקורס נראה כאן מאילו מצגות ושקפים נשלפה
          התשובה.
        </p>
      ) : (
        <ul className="context-list">
          {citations.map((c, index) => (
            <li key={index} className="context-item">
              {c}
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}

export default ContextPanel;
