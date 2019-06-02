variable "client_secret" {}

provider "azurerm" {
  subscription_id = "773c4872-6e25-452d-bcb7-a539e2c92ea7"
  client_id       = "84deea61-2f74-40c0-badf-db3af820e3ea"
  client_secret   = "${var.client_secret}"
  tenant_id       = "f90287e0-ee2a-4c9f-bc88-d8e0ef1a3950"
}

resource "azurerm_resource_group" "flairbot" {
  name     = "flairbot-rg"
  location = "northeurope"
}

resource "azurerm_storage_account" "flairbot" {
  name                     = "flairbotsa"
  resource_group_name      = "${azurerm_resource_group.flairbot.name}"
  location                 = "${azurerm_resource_group.flairbot.location}"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "flairbot" {
  name                = "flairbot-service-plan"
  location            = "${azurerm_resource_group.flairbot.location}"
  resource_group_name = "${azurerm_resource_group.flairbot.name}"

  sku {
    tier = "Free"
    size = "F1"
  }
}

resource "azurerm_function_app" "flairbot" {
  name                      = "flairbot-azure-functions"
  location                  = "${azurerm_resource_group.flairbot.location}"
  resource_group_name       = "${azurerm_resource_group.flairbot.name}"
  app_service_plan_id       = "${azurerm_app_service_plan.flairbot.id}"
  storage_connection_string = "${azurerm_storage_account.flairbot.primary_connection_string}"
  version                   = "~2"
}
