import { useState } from "react";
import { ACTION_FIELDS } from "../actionFields.js";
import { api } from "../api.js";
import Card from "./Card.jsx";
import JobConsole from "./JobConsole.jsx";

function initialValues(fields) {
  const values = {};
  for (const f of fields) {
    values[f.name] = f.type === "checkbox" ? false : f.default ?? "";
  }
  return values;
}

/** 通用 action 执行表单：根据 actionFields.js 里的字段描述渲染表单 + 执行按钮 + 实时日志。 */
export default function ActionForm({ actionId, title }) {
  const fields = ACTION_FIELDS[actionId] ?? [];
  const [values, setValues] = useState(() => initialValues(fields));
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const setField = (name, value) => setValues((v) => ({ ...v, [name]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const newJob = await api.runAction(actionId, values);
      setJob(newJob);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card title={title}>
      <form onSubmit={handleSubmit}>
        {fields.map((f) => (
          <div className="field" key={f.name}>
            {f.type === "checkbox" ? (
              <div className="field-checkbox">
                <input
                  type="checkbox"
                  id={`${actionId}-${f.name}`}
                  checked={!!values[f.name]}
                  onChange={(e) => setField(f.name, e.target.checked)}
                />
                <label htmlFor={`${actionId}-${f.name}`}>{f.label}</label>
              </div>
            ) : (
              <>
                <label htmlFor={`${actionId}-${f.name}`}>{f.label}</label>
                {f.type === "select" ? (
                  <select
                    id={`${actionId}-${f.name}`}
                    value={values[f.name]}
                    onChange={(e) => setField(f.name, e.target.value)}
                  >
                    {f.options.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt || "（默认）"}
                      </option>
                    ))}
                  </select>
                ) : f.type === "textarea" ? (
                  <textarea
                    id={`${actionId}-${f.name}`}
                    placeholder={f.placeholder}
                    value={values[f.name]}
                    onChange={(e) => setField(f.name, e.target.value)}
                  />
                ) : (
                  <input
                    id={`${actionId}-${f.name}`}
                    type={f.type === "number" ? "number" : "text"}
                    placeholder={f.placeholder}
                    value={values[f.name]}
                    onChange={(e) => setField(f.name, e.target.value)}
                  />
                )}
              </>
            )}
          </div>
        ))}
        <button className="btn" type="submit" disabled={submitting}>
          {submitting ? "启动中…" : "执行"}
        </button>
        {error && (
          <div className="muted" style={{ color: "var(--danger)", marginTop: 8 }}>
            {error}
          </div>
        )}
      </form>
      {job && (
        <div style={{ marginTop: 16 }}>
          <JobConsole job={job} />
        </div>
      )}
    </Card>
  );
}
