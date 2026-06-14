param(
  [string]$Root = "E:\agent\impact-multisession-write-gate-test",
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

function Write-Utf8File {
  param(
    [string]$Path,
    [string]$Content
  )

  $parent = Split-Path -Parent $Path
  if ($parent) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
  }

  Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Reset-ScenarioDir {
  param([string]$Path)

  $rootFull = [System.IO.Path]::GetFullPath($Root)
  $targetFull = [System.IO.Path]::GetFullPath($Path)

  if ($Clean -and (Test-Path -LiteralPath $Path)) {
    if (-not $targetFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
      throw "Refuse to remove path outside fixture root: $targetFull"
    }
    Remove-Item -LiteralPath $Path -Recurse -Force
  }

  New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Initialize-GitFixture {
  param([string]$Path)

  Push-Location $Path
  try {
    git init | Out-Null
    git config user.email "impact-write-gate@example.invalid"
    git config user.name "Impact Write Gate"
    git add .
    git commit -m "初始化写授权测试夹具" | Out-Null
  } finally {
    Pop-Location
  }
}

function New-JavaFixture {
  param(
    [string]$Path,
    [bool]$Git = $true
  )

  Reset-ScenarioDir -Path $Path

  Write-Utf8File -Path (Join-Path $Path "pom.xml") -Content @'
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>example</groupId>
  <artifactId>impact-write-gate-fixture</artifactId>
  <version>1.0.0</version>
  <properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
  </properties>
</project>
'@

  Write-Utf8File -Path (Join-Path $Path "README.md") -Content @'
# Impact Java Fixture

This fixture is intentionally small. It is used only for impact write authorization tests.

API:

- `GET /api/invoices/{id}` returns invoice id, status, amount and source.
- `GET /health` returns service status and chat capability flags.
'@

  Write-Utf8File -Path (Join-Path $Path "src/main/java/com/example/invoice/InvoiceStatus.java") -Content @'
package com.example.invoice;

public enum InvoiceStatus {
    DRAFT,
    SENT,
    PAID,
    CANCELLED
}
'@

  Write-Utf8File -Path (Join-Path $Path "src/main/java/com/example/invoice/InvoiceController.java") -Content @'
package com.example.invoice;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.Map;

public class InvoiceController {
    public Map<String, Object> getInvoice(String id) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("id", id);
        body.put("status", InvoiceStatus.PAID.name());
        body.put("amount", new BigDecimal("120.00"));
        body.put("source", "web");
        return body;
    }

    public String displayStatus(InvoiceStatus status) {
        if (status == InvoiceStatus.PAID) {
            return "Paid";
        }
        if (status == InvoiceStatus.CANCELLED) {
            return "Cancelled";
        }
        return "Open";
    }
}
'@

  Write-Utf8File -Path (Join-Path $Path "src/main/java/com/example/health/HealthController.java") -Content @'
package com.example.health;

import java.util.LinkedHashMap;
import java.util.Map;

public class HealthController {
    public Map<String, Object> health() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("status", "ok");
        body.put("service", "impact-fixture");
        body.put("chat_enabled", true);
        body.put("reference_scoring_enabled", true);
        return body;
    }
}
'@

  Write-Utf8File -Path (Join-Path $Path "src/test/java/com/example/invoice/InvoiceControllerTest.java") -Content @'
package com.example.invoice;

public class InvoiceControllerTest {
    public void getInvoiceContainsStatus() {
        InvoiceController controller = new InvoiceController();
        assert controller.getInvoice("INV-1").containsKey("status");
    }
}
'@

  if ($Git) {
    Initialize-GitFixture -Path $Path
  }
}

function New-NodeFixture {
  param([string]$Path)

  Reset-ScenarioDir -Path $Path

  Write-Utf8File -Path (Join-Path $Path "package.json") -Content @'
{
  "name": "impact-pro-node-response-fixture",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "test": "node --test",
    "lint": "node --check src/server.js"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}
'@

  Write-Utf8File -Path (Join-Path $Path "src/server.js") -Content @'
import express from "express";

export const app = express();

app.get("/api/profile/:id", (req, res) => {
  res.json({
    id: req.params.id,
    displayName: "Ada Lovelace",
    plan: "pro",
    betaAccess: false
  });
});

app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    service: "impact-pro-node-response-fixture",
    profileFieldsStable: true
  });
});
'@

  Write-Utf8File -Path (Join-Path $Path "openapi.json") -Content @'
{
  "openapi": "3.0.0",
  "paths": {
    "/api/profile/{id}": {
      "get": {
        "responses": {
          "200": {
            "description": "Profile response includes id, displayName, plan and betaAccess."
          }
        }
      }
    }
  }
}
'@

  Write-Utf8File -Path (Join-Path $Path "test/profile.test.js") -Content @'
import test from "node:test";
import assert from "node:assert/strict";

test("profile response contract", () => {
  const fields = ["id", "displayName", "plan", "betaAccess"];
  assert.ok(fields.includes("betaAccess"));
});
'@

  Initialize-GitFixture -Path $Path
}

New-Item -ItemType Directory -Force -Path $Root | Out-Null

New-JavaFixture -Path (Join-Path $Root "S1-impact-java-authorized") -Git $true
New-JavaFixture -Path (Join-Path $Root "S2-impact-java-no-confirm") -Git $true
New-JavaFixture -Path (Join-Path $Root "S3-impact-java-history-confirm") -Git $true
New-JavaFixture -Path (Join-Path $Root "S4-impact-java-delayed-confirm") -Git $true
New-JavaFixture -Path (Join-Path $Root "S5-impact-java-nongit-v1") -Git $false
New-JavaFixture -Path (Join-Path $Root "S6-impact-java-health-response") -Git $true
New-NodeFixture -Path (Join-Path $Root "S7-impact-pro-node-response")

Write-Host "Fixtures generated at $Root"
