import React, { useEffect, useRef } from "react";
import { StringArrayField } from "@js/oarepo_ui/forms";
import { useFormikContext } from "formik";
import _get from "lodash/get";
import _isEqual from "lodash/isEqual";
import { i18next } from "@translations/i18next";

const FIELD_PATH = "metadata.measurement.measurer_name";

/** Old records stored a single name as a string; arrays must not be char-split. */
export function normalizeMeasurerName(value) {
  if (value == null || value === "") {
    return [];
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed ? [trimmed] : [];
  }
  if (!Array.isArray(value)) {
    return [];
  }
  if (
    value.length > 1 &&
    value.every((item) => typeof item === "string" && item.length <= 1)
  ) {
    const joined = value.join("").trim();
    return joined ? [joined] : [];
  }
  return value
    .map((item) => (typeof item === "string" ? item.trim() : String(item)))
    .filter(Boolean);
}

export function MeasurerNameField() {
  const { values, setFieldValue } = useFormikContext();
  const lastApplied = useRef(null);

  useEffect(() => {
    const current = _get(values, FIELD_PATH);
    const normalized = normalizeMeasurerName(current);
    if (_isEqual(current, normalized)) {
      lastApplied.current = normalized;
      return;
    }
    if (_isEqual(lastApplied.current, normalized)) {
      return;
    }
    setFieldValue(FIELD_PATH, normalized);
    lastApplied.current = normalized;
  }, [values, setFieldValue]);

  return (
    <StringArrayField
      fieldPath={FIELD_PATH}
      label={i18next.t("Measurer name")}
      addButtonLabel={i18next.t("Add measurer")}
    />
  );
}
