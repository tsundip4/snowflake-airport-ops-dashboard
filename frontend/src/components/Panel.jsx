import React from "react";

function Panel({ title, children }) {
  return (
    <div className="panel">
      {title && <h2>{title}</h2>}
      {children}
    </div>
  );
}

export default Panel;
