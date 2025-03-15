"use client";

import React from "react";
import { useNotification } from "../contexts/NotificationContext";

export default function NotificationList() {
  const { notifications, removeNotification } = useNotification();

  return (
    <div style={{ position: "fixed", top: 10, right: 10, zIndex: 9999 }}>
      {notifications.map((n) => (
        <div
          key={n.id}
          style={{
            backgroundColor: n.type === "success" ? "lightgreen" : n.type === "error" ? "lightcoral" : "lightblue",
            padding: "10px 15px",
            marginBottom: "10px",
            borderRadius: 4,
            cursor: "pointer",
          }}
          onClick={() => removeNotification(n.id)}
        >
          {n.message}
        </div>
      ))}
    </div>
  );
}
