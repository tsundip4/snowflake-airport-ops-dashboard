import React from "react";

function Tabs({ tabs, active, onChange }) {
  return (
    <nav className="tabs">
      {tabs.map((tab) => (
        <button
          key={tab}
          className={tab === active ? "active" : ""}
          onClick={() => onChange(tab)}
        >
          {tab[0].toUpperCase() + tab.slice(1)}
        </button>
      ))}
    </nav>
  );
}

export default Tabs;
