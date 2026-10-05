import type { Language } from "@hellodesk/shared/api-types";

export interface GuestStayMessages {
  amount: string;
  arrival: string;
  barcodeNote: string;
  bill: string;
  billHelp: string;
  cancel: string;
  cancelAction: string;
  checkIn: string;
  checkInComplete: string;
  checkOut: string;
  checkoutComplete: string;
  confirm: string;
  confirmReservation: string;
  continue: string;
  confirmHeading: string;
  confirming: string;
  departure: string;
  endSession: string;
  expiration: string;
  guest: string;
  item: string;
  lookup: string;
  quantity: string;
  reservationCode: string;
  reservationDetails: string;
  reviewRequired: string;
  requestComplete: string;
  requestUpdate: string;
  room: string;
  stayReady: string;
  total: string;
  welcome: string;
}

const ENGLISH_MESSAGES: GuestStayMessages = {
  amount: "Amount",
  arrival: "Arrival",
  barcodeNote: "This display-only barcode is not a door credential.",
  bill: "Review your bill",
  billHelp: "Review every charge before confirming checkout. No payment is collected here.",
  cancel: "Cancel",
  cancelAction: "Cancel request",
  checkIn: "Check in",
  checkInComplete: "Check-in is complete.",
  checkOut: "Confirm checkout",
  checkoutComplete: "Checkout is complete. No payment was collected.",
  confirm: "Confirm",
  confirmHeading: "Please confirm this request",
  confirmReservation: "Confirm reservation details",
  confirming: "Confirming…",
  continue: "Continue",
  departure: "Departure",
  endSession: "End session",
  expiration: "This request expires at",
  guest: "Guest",
  item: "Item",
  lookup: "Find reservation",
  quantity: "Qty.",
  reservationCode: "Reservation code",
  reservationDetails: "Reservation details",
  reviewRequired: "Review required",
  requestComplete: "Request complete",
  requestUpdate: "Request update",
  room: "Your room",
  stayReady: "Your stay is ready for the next step.",
  total: "Total",
  welcome: "Welcome to HelloDesk",
};

const VIETNAMESE_MESSAGES: GuestStayMessages = {
  amount: "Số tiền",
  arrival: "Ngày đến",
  barcodeNote: "Mã vạch chỉ để hiển thị và không dùng làm chìa khóa phòng.",
  bill: "Xem lại hóa đơn của bạn",
  billHelp: "Vui lòng xem từng khoản phí trước khi xác nhận trả phòng. Không có thanh toán tại đây.",
  cancel: "Hủy",
  cancelAction: "Hủy yêu cầu",
  checkIn: "Nhận phòng",
  checkInComplete: "Bạn đã nhận phòng thành công.",
  checkOut: "Xác nhận trả phòng",
  checkoutComplete: "Bạn đã trả phòng. Không có khoản thanh toán nào được thu.",
  confirm: "Xác nhận",
  confirmHeading: "Vui lòng xác nhận yêu cầu này",
  confirmReservation: "Xác nhận thông tin đặt phòng",
  confirming: "Đang xác nhận…",
  continue: "Tiếp tục",
  departure: "Ngày đi",
  endSession: "Kết thúc phiên",
  expiration: "Yêu cầu này hết hạn lúc",
  guest: "Khách",
  item: "Khoản mục",
  lookup: "Tìm đặt phòng",
  quantity: "Số lượng",
  reservationCode: "Mã đặt phòng",
  reservationDetails: "Thông tin đặt phòng",
  reviewRequired: "Vui lòng xem lại",
  requestComplete: "Yêu cầu đã hoàn tất",
  requestUpdate: "Cập nhật yêu cầu",
  room: "Phòng của bạn",
  stayReady: "Thông tin lưu trú của bạn đã sẵn sàng cho bước tiếp theo.",
  total: "Tổng cộng",
  welcome: "Chào mừng đến với HelloDesk",
};

export function getGuestStayMessages(language: Language): GuestStayMessages {
  return language === "vi" ? VIETNAMESE_MESSAGES : ENGLISH_MESSAGES;
}
