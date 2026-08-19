export const number = (value: number) => new Intl.NumberFormat("en-IE").format(value);
export const money = (value: number) => new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(value);
export const percent = (value: number) => `${value.toFixed(2)}%`;
