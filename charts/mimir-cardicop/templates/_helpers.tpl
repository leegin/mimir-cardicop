{{- define "mimir-cardicop.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{ .Values.fullnameOverride }}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "mimir-cardicop.serviceAccountName" -}}
{{- if .Values.serviceAccount.name -}}
{{ .Values.serviceAccount.name }}
{{- else -}}
{{ include "mimir-cardicop.fullname" . }}
{{- end -}}
{{- end -}}

{{- define "mimir-cardicop.labels" -}}
app.kubernetes.io/name: {{ include "mimir-cardicop.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- toYaml .Values.labels | nindent 0}}
{{- end -}}

{{- define "mimir-cardicop.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mimir-cardicop.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}