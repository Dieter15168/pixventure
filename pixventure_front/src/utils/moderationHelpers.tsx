// src/utils/moderationHelpers.tsx
/**
 * Returns style modifications based on the moderation status.
 *
 * @param {string | undefined} status - The moderation status of the element.
 * @returns {React.CSSProperties} - The style modifications for the element.
 */
export function getStatusStyle(status?: string): React.CSSProperties {
    if (!status) return {};
    switch (status.toLowerCase()) {
      case "approved":
        return { borderLeft: "4px solid green", backgroundColor: "#e6ffe6" };
      case "rejected":
        return { borderLeft: "4px solid red", backgroundColor: "#ffe6e6" };
      default:
        return {}; // "Pending moderation" or other statuses show a transparent background.
    }
  }
  