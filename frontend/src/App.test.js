import React from "react";
import { render } from "@testing-library/react";
import App from "./App";

test("renders learn react link", () => {
  const { getByText } = render(<App />);
  const linkElement = getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});

test("renders fail link", () => {
  const { getByText } = render(<App />);
  const linkElement = getByText(/I am a negative test/i);
  expect(linkElement).toBeInTheDocument();
});
