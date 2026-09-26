package com.gachiguild.gachitoefl.data.billing

import android.app.Activity
import android.content.Context
import com.gachiguild.gachitoefl.BuildConfig
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import com.android.billingclient.api.Purchase
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

enum class PremiumAccess {
    UNKNOWN,
    LOCKED,
    UNLOCKED
}

enum class PremiumBillingMessage {
    NONE,
    SUCCESS,
    PENDING,
    ERROR
}

data class PremiumBillingState(
    val access: PremiumAccess = PremiumAccess.UNKNOWN,
    val productPrice: String? = null,
    val isLoading: Boolean = true,
    val isPurchasing: Boolean = false,
    val message: PremiumBillingMessage = PremiumBillingMessage.NONE
)

/**
 * プレミアム機能の実効的な解放状態。
 *
 * productionDebug/release では Google Play で購入済み（PURCHASED）の場合だけ解放する。
 * 通常の debug ビルドでは QA 用に無条件で解放する。
 */
fun PremiumBillingState.isPremiumUnlocked(): Boolean =
    access.isPremiumUnlocked()

fun PremiumAccess.isPremiumUnlocked(): Boolean =
    !BuildConfig.PRODUCTION_MODE || this == PremiumAccess.UNLOCKED

/** Google Play の買い切り商品で TOEFL の上位レベルを解放する処理。 */
@Singleton
class PremiumBillingManager @Inject constructor(
    @ApplicationContext context: Context
) : PurchasesUpdatedListener {

    companion object {
        /** Play Console で作成する非消費型（一度購入すれば永久解放）商品ID。 */
        const val PRODUCT_ID = "toefl_premium_levels_unlock"
    }

    private val _state = MutableStateFlow(PremiumBillingState())
    val state: StateFlow<PremiumBillingState> = _state.asStateFlow()

    private val billingClient = BillingClient.newBuilder(context)
        .setListener(this)
        .enablePendingPurchases(
            PendingPurchasesParams.newBuilder()
                .enableOneTimeProducts()
                .build()
        )
        .enableAutoServiceReconnection()
        .build()

    private var productDetails: ProductDetails? = null
    private var connectionInProgress = false

    init {
        refresh()
    }

    /** アプリ起動時・復帰時に商品情報と購入状態を再確認する。 */
    fun refresh() {
        _state.update {
            it.copy(
                isLoading = true,
                isPurchasing = false,
                message = PremiumBillingMessage.NONE
            )
        }

        if (billingClient.isReady) {
            queryProductDetails()
            queryPurchases()
            return
        }

        if (connectionInProgress) return
        connectionInProgress = true
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(billingResult: BillingResult) {
                connectionInProgress = false
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    queryProductDetails()
                    queryPurchases()
                } else {
                    setError()
                }
            }

            override fun onBillingServiceDisconnected() {
                connectionInProgress = false
                _state.update {
                    it.copy(isLoading = false, access = PremiumAccess.UNKNOWN)
                }
            }
        })
    }

    private fun queryProductDetails() {
        val params = QueryProductDetailsParams.newBuilder()
            .setProductList(
                listOf(
                    QueryProductDetailsParams.Product.newBuilder()
                        .setProductId(PRODUCT_ID)
                        .setProductType(BillingClient.ProductType.INAPP)
                        .build()
                )
            )
            .build()

        billingClient.queryProductDetailsAsync(params) { billingResult, result ->
            if (billingResult.responseCode != BillingClient.BillingResponseCode.OK) {
                setError()
                return@queryProductDetailsAsync
            }

            productDetails = result.productDetailsList.firstOrNull { it.productId == PRODUCT_ID }
            val offer = productDetails?.oneTimePurchaseOfferDetailsList?.firstOrNull()
            val formattedPrice = offer?.formattedPrice
                ?: productDetails?.oneTimePurchaseOfferDetails?.formattedPrice
            _state.update {
                it.copy(
                    productPrice = formattedPrice,
                    isLoading = false,
                    message = if (productDetails == null) {
                        PremiumBillingMessage.ERROR
                    } else {
                        PremiumBillingMessage.NONE
                    }
                )
            }
        }
    }

    private fun queryPurchases() {
        val params = QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.INAPP)
            .build()

        billingClient.queryPurchasesAsync(params) { billingResult, purchases ->
            if (billingResult.responseCode != BillingClient.BillingResponseCode.OK) {
                setError()
                return@queryPurchasesAsync
            }
            processPurchases(purchases, notifySuccess = false)
        }
    }

    fun purchase(activity: Activity) {
        val details = productDetails
        if (details == null) {
            refresh()
            return
        }

        _state.update {
            it.copy(isPurchasing = true, message = PremiumBillingMessage.NONE)
        }

        val offerToken = details.oneTimePurchaseOfferDetailsList?.firstOrNull()?.offerToken
        val productParams = BillingFlowParams.ProductDetailsParams.newBuilder()
            .setProductDetails(details)
            .apply {
                if (!offerToken.isNullOrBlank()) setOfferToken(offerToken)
            }
            .build()
        val flowParams = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(listOf(productParams))
            .build()

        val billingResult = billingClient.launchBillingFlow(activity, flowParams)
        if (billingResult.responseCode != BillingClient.BillingResponseCode.OK) {
            _state.update {
                it.copy(isPurchasing = false, message = PremiumBillingMessage.ERROR)
            }
        }
    }

    override fun onPurchasesUpdated(
        billingResult: BillingResult,
        purchases: MutableList<Purchase>?
    ) {
        when (billingResult.responseCode) {
            BillingClient.BillingResponseCode.OK -> {
                processPurchases(purchases.orEmpty(), notifySuccess = true)
            }
            BillingClient.BillingResponseCode.USER_CANCELED -> {
                _state.update { it.copy(isPurchasing = false) }
            }
            else -> {
                _state.update {
                    it.copy(isPurchasing = false, message = PremiumBillingMessage.ERROR)
                }
            }
        }
    }

    private fun processPurchases(purchases: List<Purchase>, notifySuccess: Boolean) {
        val premiumPurchase = purchases.firstOrNull { PRODUCT_ID in it.products }
        when {
            premiumPurchase?.purchaseState == Purchase.PurchaseState.PURCHASED -> {
                _state.update {
                    it.copy(
                        access = PremiumAccess.UNLOCKED,
                        isLoading = false,
                        isPurchasing = false,
                        message = if (notifySuccess) {
                            PremiumBillingMessage.SUCCESS
                        } else {
                            PremiumBillingMessage.NONE
                        }
                    )
                }
                acknowledgeIfNeeded(premiumPurchase)
            }
            premiumPurchase?.purchaseState == Purchase.PurchaseState.PENDING -> {
                _state.update {
                    it.copy(
                        access = PremiumAccess.LOCKED,
                        isLoading = false,
                        isPurchasing = false,
                        message = PremiumBillingMessage.PENDING
                    )
                }
            }
            else -> {
                _state.update {
                    it.copy(
                        access = PremiumAccess.LOCKED,
                        isLoading = false,
                        isPurchasing = false
                    )
                }
            }
        }
    }

    private fun acknowledgeIfNeeded(purchase: Purchase) {
        if (purchase.isAcknowledged) return
        val params = AcknowledgePurchaseParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken)
            .build()
        billingClient.acknowledgePurchase(params) { billingResult ->
            if (billingResult.responseCode != BillingClient.BillingResponseCode.OK) {
                // 次回の照会時に未承認なら再試行する。解放状態は購入確認済みのため維持する。
                _state.update { it.copy(message = PremiumBillingMessage.ERROR) }
            }
        }
    }

    fun clearMessage() {
        _state.update { it.copy(message = PremiumBillingMessage.NONE) }
    }

    private fun setError() {
        _state.update {
            it.copy(
                access = PremiumAccess.UNKNOWN,
                isLoading = false,
                isPurchasing = false,
                message = PremiumBillingMessage.ERROR
            )
        }
    }
}
