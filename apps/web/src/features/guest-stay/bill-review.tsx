"use client";

import type { Bill, Language } from "@hellodesk/shared/api-types";

import { getGuestStayMessages } from "./messages";

interface BillReviewProps {
  bill: Bill;
  language: Language;
  isPreparing?: boolean;
  onPrepareCheckout: () => void;
}

function formatMoney(amountMinor: number, currency: string, language: Language): string {
  return new Intl.NumberFormat(language === "vi" ? "vi-VN" : "en-US", {
    style: "currency",
    currency,
  }).format(amountMinor / 100);
}

export function BillReview({ bill, language, isPreparing, onPrepareCheckout }: BillReviewProps) {
  const messages = getGuestStayMessages(language);
  return (
    <section className="bill-card" aria-labelledby="bill-heading">
      <h2 id="bill-heading">{messages.bill}</h2>
      <p>{messages.billHelp}</p>
      <table>
        <thead>
          <tr>
            <th scope="col">{messages.item}</th>
            <th scope="col">{messages.quantity}</th>
            <th scope="col">{messages.amount}</th>
          </tr>
        </thead>
        <tbody>
          {bill.items.map((item) => (
            <tr key={`${item.description}-${item.lineTotalMinor}`}>
              <td>{item.description}</td>
              <td>{item.quantity}</td>
              <td>{formatMoney(item.lineTotalMinor, bill.currency, language)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={2} scope="row">{messages.total}</th>
            <td>{formatMoney(bill.totalAmountMinor, bill.currency, language)}</td>
          </tr>
        </tfoot>
      </table>
      <button type="button" disabled={isPreparing} onClick={onPrepareCheckout}>
        {isPreparing ? "Preparing…" : messages.checkOut}
      </button>
    </section>
  );
}
