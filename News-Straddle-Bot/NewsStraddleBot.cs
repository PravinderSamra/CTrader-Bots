// =============================================================================
// News Straddle Bot - Pre-news volatility straddle with manual OCO emulation
// Single compilable .cs file for cTrader Automate
// See SPEC.md for the full design specification this build implements.
// =============================================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    // =========================================================================
    // ENUMS
    // =========================================================================

    public enum RiskModeEnum
    {
        PercentOfEquity,
        FixedAmount
    }

    public enum NewsTimeZoneEnum
    {
        NewYork,
        LondonUK,
        Frankfurt,
        Tokyo,
        Singapore,
        HongKong
    }

    public enum OrderExecutionTypeEnum
    {
        StopMarket,
        StopLimit
    }

    public enum TriggerSideEnum
    {
        Standard,
        OppositeSide
    }

    public enum SpreadGuardModeEnum
    {
        ProceedAnyway,
        AutoWidenBuffer,
        SkipTrade
    }

    public enum DoubleFillPolicyEnum
    {
        FlattenBoth,
        KeepBetterPriced,
        KeepFirstFilled
    }

    public enum BotStateEnum
    {
        Idle,
        Arming,
        PlacingOrders,
        ArmedWaiting,
        Filled,
        TimedOut,
        Skipped,
        ErrorState,
        Complete
    }

    // =========================================================================
    // PER-POSITION STATE (ratchet design adapted from the ORB Breakout bot's
    // ProcessDynamicStop / PositionState pattern, per SPEC.md 5.5/6a)
    // =========================================================================

    public class StraddlePositionState
    {
        public long PositionId { get; set; }
        public double EntryPrice { get; set; }
        public double InitialRiskInPriceUnits { get; set; }
        public double LastTrailSteps { get; set; }
        public TradeType TradeType { get; set; }
    }

    // =========================================================================
    // MAIN CBOT CLASS
    // =========================================================================

    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class NewsStraddleBot : Robot
    {
        // =====================================================================
        // PARAMETERS (SPEC.md section 3)
        // =====================================================================

        // ----- 3.1 Risk & Sizing -----
        [Parameter("Risk Mode", Group = "Risk & Sizing", DefaultValue = RiskModeEnum.PercentOfEquity)]
        public RiskModeEnum RiskMode { get; set; }

        [Parameter("Risk Percent", Group = "Risk & Sizing", DefaultValue = 0.5, MinValue = 0.01)]
        public double RiskPercent { get; set; }

        [Parameter("Risk Fixed Amount", Group = "Risk & Sizing", DefaultValue = 100, MinValue = 0.01)]
        public double RiskFixedAmount { get; set; }

        [Parameter("Max Lot Cap (0 = off)", Group = "Risk & Sizing", DefaultValue = 0, MinValue = 0)]
        public double MaxLotCap { get; set; }

        [Parameter("Slippage Buffer Percent", Group = "Risk & Sizing", DefaultValue = 30, MinValue = 0)]
        public double SlippageBufferPercent { get; set; }

        // ----- 3.2 News Timing -----
        [Parameter("News Date/Time (wall clock in zone below)", Group = "News Timing")]
        public DateTime NewsDateTime { get; set; }

        [Parameter("News Time Zone", Group = "News Timing", DefaultValue = NewsTimeZoneEnum.NewYork)]
        public NewsTimeZoneEnum NewsTimeZone { get; set; }

        [Parameter("Entry Lead Minutes", Group = "News Timing", DefaultValue = 2, MinValue = 1, MaxValue = 10)]
        public int EntryLeadMinutes { get; set; }

        [Parameter("Order Timeout Minutes", Group = "News Timing", DefaultValue = 10, MinValue = 1)]
        public int OrderTimeoutMinutes { get; set; }

        // ----- 3.3 Entry Structure -----
        [Parameter("Buffer Distance (pips/points)", Group = "Entry Structure", DefaultValue = 10, MinValue = 0.1)]
        public double BufferDistance { get; set; }

        [Parameter("Order Execution Type", Group = "Entry Structure", DefaultValue = OrderExecutionTypeEnum.StopMarket)]
        public OrderExecutionTypeEnum OrderExecutionType { get; set; }

        [Parameter("Stop-Limit Range (pips)", Group = "Entry Structure", DefaultValue = 5, MinValue = 0.1)]
        public double StopLimitRangePips { get; set; }

        [Parameter("Trigger Side", Group = "Entry Structure", DefaultValue = TriggerSideEnum.OppositeSide)]
        public TriggerSideEnum TriggerSide { get; set; }

        [Parameter("Expected Release Spread (pips/points)", Group = "Entry Structure", DefaultValue = 15, MinValue = 0)]
        public double ExpectedReleaseSpread { get; set; }

        // ----- 3.4 Spread Guard -----
        [Parameter("Spread Guard Mode", Group = "Spread Guard", DefaultValue = SpreadGuardModeEnum.ProceedAnyway)]
        public SpreadGuardModeEnum SpreadGuardMode { get; set; }

        [Parameter("Spread Guard Threshold (x avg)", Group = "Spread Guard", DefaultValue = 3.0, MinValue = 1.0)]
        public double SpreadGuardThreshold { get; set; }

        [Parameter("Spread Widen Factor", Group = "Spread Guard", DefaultValue = 1.5, MinValue = 1.0)]
        public double SpreadWidenFactor { get; set; }

        // ----- 3.5 Stop Loss / Take Profit -----
        [Parameter("Stop Loss Distance (pips/points)", Group = "Stop Loss / Take Profit", DefaultValue = 20, MinValue = 0.1)]
        public double StopLossDistance { get; set; }

        [Parameter("Enable Take Profit", Group = "Stop Loss / Take Profit", DefaultValue = true)]
        public bool EnableTakeProfit { get; set; }

        [Parameter("Take Profit (R multiple)", Group = "Stop Loss / Take Profit", DefaultValue = 2.0, MinValue = 0.1)]
        public double TakeProfitR { get; set; }

        // ----- 3.6 Dynamic (Trailing) Stop -----
        [Parameter("Enable Dynamic Stop", Group = "Dynamic Stop", DefaultValue = false)]
        public bool EnableDynamicStop { get; set; }

        [Parameter("Dynamic Stop Activation (R)", Group = "Dynamic Stop", DefaultValue = 0.25, MinValue = 0)]
        public double DynamicStopActivationR { get; set; }

        [Parameter("Dynamic Stop Trail Step (R)", Group = "Dynamic Stop", DefaultValue = 0.25, MinValue = 0.01)]
        public double DynamicStopTrailR { get; set; }

        [Parameter("Dynamic Stop Extra Pips", Group = "Dynamic Stop", DefaultValue = 0.0, MinValue = 0)]
        public double DynamicStopExtraPips { get; set; }

        // ----- 3.6a Double-Fill Handling -----
        [Parameter("Double-Fill Policy", Group = "Double-Fill Handling", DefaultValue = DoubleFillPolicyEnum.FlattenBoth)]
        public DoubleFillPolicyEnum DoubleFillPolicy { get; set; }

        // ----- 3.8 Diagnostics / Safety -----
        [Parameter("Enable Chart Labels", Group = "Diagnostics / Safety", DefaultValue = true)]
        public bool EnableChartLabels { get; set; }

        [Parameter("Enable Detailed Logging", Group = "Diagnostics / Safety", DefaultValue = true)]
        public bool EnableDetailedLogging { get; set; }

        // =====================================================================
        // INTERNAL STATE
        // =====================================================================

        private const string LabelPrefix = "NewsStraddle";
        private const int SpreadBaselineWindowMinutes = 30;

        private BotStateEnum _state = BotStateEnum.Idle;
        private DateTime _newsTimeUtc = DateTime.MinValue;
        private DateTime? _lastArmedNewsTimeUtc;
        private string _runId = "";

        private bool _isPointBased;
        private StopTriggerMethod _triggerMethod;

        private PendingOrder _buyOrder;
        private PendingOrder _sellOrder;
        private bool _buyOrderPlaced, _sellOrderPlaced, _buyOrderFailed, _sellOrderFailed;
        private bool _cancelBuyOnConfirm, _cancelSellOnConfirm;

        private Dictionary<long, StraddlePositionState> _positionStates;
        private Queue<KeyValuePair<DateTime, double>> _spreadSamples;

        // =====================================================================
        // LIFECYCLE
        // =====================================================================

        protected override void OnStart()
        {
            _isPointBased = DetectIsPointBased();
            _triggerMethod = TriggerSide == TriggerSideEnum.OppositeSide ? StopTriggerMethod.Opposite : StopTriggerMethod.Trade;
            _positionStates = new Dictionary<long, StraddlePositionState>();
            _spreadSamples = new Queue<KeyValuePair<DateTime, double>>();

            Positions.Opened += OnPositionOpened;
            Positions.Closed += OnPositionClosed;
            PendingOrders.Filled += OnPendingOrderFilled;
            PendingOrders.Cancelled += OnPendingOrderCancelled;

            ResumeExistingState();

            Timer.Start(TimeSpan.FromSeconds(1));

            Log("STARTED. Symbol={0} PointBased={1} TriggerSide={2} (StopTriggerMethod.{3}) DoubleFillPolicy={4}",
                SymbolName, _isPointBased, TriggerSide, _triggerMethod, DoubleFillPolicy);

            if (EnableDynamicStop && EnableTakeProfit && TakeProfitR <= DynamicStopActivationR)
                Log("WARNING: TakeProfitR ({0}) <= DynamicStopActivationR ({1}). TP will cap the trade before the dynamic stop gets much room to trail.",
                    TakeProfitR, DynamicStopActivationR);
        }

        protected override void OnTimer()
        {
            UpdateSpreadSample();

            if (_state == BotStateEnum.Idle)
                TryArmForNextEvent();

            UpdateChartLabel();
        }

        protected override void OnTick()
        {
            ManageOpenPositions();
        }

        protected override void OnStop()
        {
            Positions.Opened -= OnPositionOpened;
            Positions.Closed -= OnPositionClosed;
            PendingOrders.Filled -= OnPendingOrderFilled;
            PendingOrders.Cancelled -= OnPendingOrderCancelled;
            Timer.Stop();
            Log("STOPPED.");
        }

        // =====================================================================
        // PRE-FLIGHT / RESUME (SPEC.md 6 - "bot re-added mid-cycle")
        // =====================================================================

        private void ResumeExistingState()
        {
            var existingPosition = FindBotPosition();
            if (existingPosition != null)
            {
                RegisterPosition(existingPosition);
                _state = BotStateEnum.Filled;
                Log("RESUME: Found existing bot position {0}. Resuming FILLED state for dynamic-stop management.", existingPosition.Id);
                return;
            }

            var existingBuy = FindPendingOrderByPrefix(TradeType.Buy);
            var existingSell = FindPendingOrderByPrefix(TradeType.Sell);

            if (existingBuy != null && existingSell != null)
            {
                _buyOrder = existingBuy;
                _sellOrder = existingSell;
                _buyOrderPlaced = _sellOrderPlaced = true;
                _state = BotStateEnum.ArmedWaiting;
                Log("RESUME: Found an existing live order pair. Resuming ARMED_WAITING state.");
                return;
            }

            if (existingBuy != null || existingSell != null)
            {
                var orphan = existingBuy ?? existingSell;
                Log("WARNING: Found an orphaned single pending order (Id={0}) with no sibling. Cancelling it to avoid a naked one-sided straddle.", orphan.Id);
                CancelPendingOrderAsync(orphan, r => { });
            }

            _state = BotStateEnum.Idle;
        }

        // =====================================================================
        // STATE MACHINE - ARMING (SPEC.md section 4)
        // =====================================================================

        private void TryArmForNextEvent()
        {
            DateTime newsUtc;
            if (!TryComputeNewsTimeUtc(out newsUtc))
                return;

            if (_lastArmedNewsTimeUtc.HasValue && _lastArmedNewsTimeUtc.Value == newsUtc)
                return;

            DateTime armUtc = newsUtc.AddMinutes(-EntryLeadMinutes);
            DateTime staleUtc = newsUtc.AddMinutes(OrderTimeoutMinutes);

            if (Server.TimeInUtc >= staleUtc)
            {
                _lastArmedNewsTimeUtc = newsUtc;
                Log("SKIPPED: NewsDateTime {0:yyyy-MM-dd HH:mm} UTC is already stale (past its timeout window). Set a future NewsDateTime for the next event.", newsUtc);
                return;
            }

            if (Server.TimeInUtc < armUtc)
                return;

            _newsTimeUtc = newsUtc;
            _lastArmedNewsTimeUtc = newsUtc;
            _runId = newsUtc.ToString("yyyyMMddHHmmss");
            _state = BotStateEnum.Arming;
            Log("STATE: IDLE -> ARMING. NewsTimeUtc={0:yyyy-MM-dd HH:mm:ss} ArmTimeUtc={1:yyyy-MM-dd HH:mm:ss}", newsUtc, armUtc);

            RunPreflightAndArm();
        }

        private void RunPreflightAndArm()
        {
            if (FindBotPosition() != null || FindPendingOrderByPrefix(TradeType.Buy) != null || FindPendingOrderByPrefix(TradeType.Sell) != null)
            {
                Log("ERROR: Pre-flight found an existing bot position/order already active. Refusing to arm a duplicate straddle.");
                Log("STATE: ARMING -> ERROR_STATE.");
                _state = BotStateEnum.ErrorState;
                _state = BotStateEnum.Idle;
                return;
            }

            if (!IsNewsTimeWithinTradingSession(_newsTimeUtc))
                Log("WARNING: NewsDateTime {0:yyyy-MM-dd HH:mm} UTC falls outside {1}'s known trading session.", _newsTimeUtc, SymbolName);

            // Highest-severity check in the spec (5.7): a tight Standard-side buffer during a
            // spread blowout can trigger both legs from spread widening alone, with no real move.
            if (TriggerSide == TriggerSideEnum.Standard && BufferDistance < 2 * ExpectedReleaseSpread)
                Log("WARNING: TriggerSide=Standard with BufferDistance ({0}) < 2x ExpectedReleaseSpread ({1}). Spread-triggered double fills at release are LIKELY. Consider TriggerSide=OppositeSide.",
                    BufferDistance, ExpectedReleaseSpread);

            double effectiveBuffer = BufferDistance;

            double currentSpread = CurrentSpreadPips();
            double avgSpread = GetRollingAverageSpreadPips();
            bool spreadAbnormal = avgSpread > 0 && currentSpread > avgSpread * SpreadGuardThreshold;

            double minDistancePrice = GetBrokerMinStopDistancePrice();
            bool bufferBelowMin = minDistancePrice > 0 && ToPriceDistance(effectiveBuffer) < minDistancePrice;
            bool slBelowMin = minDistancePrice > 0 && ToPriceDistance(StopLossDistance) < minDistancePrice;

            if (spreadAbnormal)
                Log("SPREAD GUARD: Current spread {0:F1} vs {1:F1}x average ({2:F1}). Mode={3}.", currentSpread, SpreadGuardThreshold, avgSpread, SpreadGuardMode);

            if (bufferBelowMin || slBelowMin)
                Log("MIN DISTANCE GUARD: BufferDistance/StopLossDistance is inside the broker's minimum stop distance ({0}). Mode={1}.", FormatPrice(minDistancePrice), SpreadGuardMode);

            if (spreadAbnormal || bufferBelowMin || slBelowMin)
            {
                switch (SpreadGuardMode)
                {
                    case SpreadGuardModeEnum.SkipTrade:
                        Log("STATE: ARMING -> SKIPPED (SpreadGuardMode=SkipTrade).");
                        _state = BotStateEnum.Skipped;
                        _state = BotStateEnum.Idle;
                        return;

                    case SpreadGuardModeEnum.AutoWidenBuffer:
                        effectiveBuffer = BufferDistance * SpreadWidenFactor;
                        if (ToPriceDistance(effectiveBuffer) < minDistancePrice)
                            effectiveBuffer = (minDistancePrice * 1.1) / (_isPointBased ? Symbol.TickSize : Symbol.PipSize);
                        Log("SPREAD GUARD: AutoWidenBuffer applied. Buffer {0} -> {1:F2}.", BufferDistance, effectiveBuffer);
                        break;

                    case SpreadGuardModeEnum.ProceedAnyway:
                    default:
                        Log("SPREAD GUARD: ProceedAnyway - placing orders despite the warning above.");
                        break;
                }
            }

            PlaceStraddleOrders(effectiveBuffer);
        }

        // =====================================================================
        // ORDER PLACEMENT / OCO EMULATION (SPEC.md 5.1)
        // =====================================================================

        private void PlaceStraddleOrders(double effectiveBufferUserUnits)
        {
            _state = BotStateEnum.PlacingOrders;
            Log("STATE: ARMING -> PLACING_ORDERS.");

            double bufferPrice = ToPriceDistance(effectiveBufferUserUnits);
            double slPriceDistance = ToPriceDistance(StopLossDistance);
            double sizingSlPips = (slPriceDistance / Symbol.PipSize) * (1.0 + SlippageBufferPercent / 100.0);

            double volume = ComputeVolume(sizingSlPips);
            if (volume <= 0)
            {
                Log("ERROR: Computed volume <= 0. Aborting this arm cycle.");
                Log("STATE: PLACING_ORDERS -> ERROR_STATE.");
                _state = BotStateEnum.ErrorState;
                _state = BotStateEnum.Idle;
                return;
            }

            double buyEntry = RoundToTick(Symbol.Ask + bufferPrice);
            double sellEntry = RoundToTick(Symbol.Bid - bufferPrice);

            double buySl = RoundToTick(buyEntry - slPriceDistance);
            double sellSl = RoundToTick(sellEntry + slPriceDistance);

            double? buyTp = null, sellTp = null;
            if (EnableTakeProfit)
            {
                double tpDistance = slPriceDistance * TakeProfitR;
                buyTp = RoundToTick(buyEntry + tpDistance);
                sellTp = RoundToTick(sellEntry - tpDistance);
            }

            DateTime expiration = _newsTimeUtc.AddMinutes(OrderTimeoutMinutes);

            string buyLabel = string.Format("{0}_Buy_{1}", LabelPrefix, _runId);
            string sellLabel = string.Format("{0}_Sell_{1}", LabelPrefix, _runId);

            _buyOrderPlaced = false; _sellOrderPlaced = false; _buyOrderFailed = false; _sellOrderFailed = false;
            _cancelBuyOnConfirm = false; _cancelSellOnConfirm = false;
            _buyOrder = null; _sellOrder = null;

            PlaceLeg(TradeType.Buy, buyEntry, buySl, buyTp, volume, expiration, buyLabel,
                result => HandleOrderPlacementResult(result, true));

            PlaceLeg(TradeType.Sell, sellEntry, sellSl, sellTp, volume, expiration, sellLabel,
                result => HandleOrderPlacementResult(result, false));

            Log("ORDERS SUBMITTED: Buy stop {0} SL={1} TP={2} | Sell stop {3} SL={4} TP={5} | Volume={6} Expiry={7:yyyy-MM-dd HH:mm:ss}",
                FormatPrice(buyEntry), FormatPrice(buySl), buyTp.HasValue ? FormatPrice(buyTp.Value) : "-",
                FormatPrice(sellEntry), FormatPrice(sellSl), sellTp.HasValue ? FormatPrice(sellTp.Value) : "-",
                volume, expiration);
        }

        private void PlaceLeg(TradeType type, double targetPrice, double? sl, double? tp, double volume, DateTime expiration, string label, Action<TradeResult> callback)
        {
            if (OrderExecutionType == OrderExecutionTypeEnum.StopLimit)
            {
                PlaceStopLimitOrderAsync(
                    tradeType: type,
                    symbolName: SymbolName,
                    volume: volume,
                    targetPrice: targetPrice,
                    stopLimitRangePips: StopLimitRangePips,
                    label: label,
                    stopLoss: sl,
                    takeProfit: tp,
                    protectionType: ProtectionType.Absolute,
                    expiration: expiration,
                    comment: _runId,
                    hasTrailingStop: false,
                    stopLossTriggerMethod: _triggerMethod,
                    stopOrderTriggerMethod: _triggerMethod,
                    callback: callback);
            }
            else
            {
                PlaceStopOrderAsync(
                    tradeType: type,
                    symbolName: SymbolName,
                    volume: volume,
                    targetPrice: targetPrice,
                    label: label,
                    stopLoss: sl,
                    takeProfit: tp,
                    protectionType: ProtectionType.Absolute,
                    expiration: expiration,
                    comment: _runId,
                    hasTrailingStop: false,
                    stopLossTriggerMethod: _triggerMethod,
                    stopOrderTriggerMethod: _triggerMethod,
                    callback: callback);
            }
        }

        private void HandleOrderPlacementResult(TradeResult result, bool isBuyLeg)
        {
            if (result.IsSuccessful)
            {
                if (isBuyLeg) { _buyOrder = result.PendingOrder; _buyOrderPlaced = true; }
                else { _sellOrder = result.PendingOrder; _sellOrderPlaced = true; }
                Log("ORDER PLACED: {0} leg confirmed. Id={1}", isBuyLeg ? "Buy" : "Sell", result.PendingOrder != null ? result.PendingOrder.Id.ToString() : "?");

                // Closes a rare async race: the sibling leg may already have filled and tried to
                // cancel this order before this placement callback even confirmed it existed.
                bool shouldCancelNow = isBuyLeg ? _cancelBuyOnConfirm : _cancelSellOnConfirm;
                if (shouldCancelNow && result.PendingOrder != null)
                {
                    Log("The sibling leg already filled before this leg's placement confirmed. Cancelling this {0} leg now.", isBuyLeg ? "Buy" : "Sell");
                    CancelPendingOrderAsync(result.PendingOrder, r => { });
                }
            }
            else
            {
                if (isBuyLeg) _buyOrderFailed = true; else _sellOrderFailed = true;
                Log("ERROR: {0} leg placement FAILED. Reason={1}", isBuyLeg ? "Buy" : "Sell", result.Error);
            }

            EvaluatePlacementOutcome();
        }

        private void EvaluatePlacementOutcome()
        {
            if (_state != BotStateEnum.PlacingOrders) return;

            bool buyDone = _buyOrderPlaced || _buyOrderFailed;
            bool sellDone = _sellOrderPlaced || _sellOrderFailed;
            if (!buyDone || !sellDone) return;

            if (_buyOrderPlaced && _sellOrderPlaced)
            {
                _state = BotStateEnum.ArmedWaiting;
                Log("STATE: PLACING_ORDERS -> ARMED_WAITING. Both legs live.");
                return;
            }

            Log("ERROR: Partial placement failure (kill-switch). Cancelling whichever leg succeeded to avoid a naked one-sided straddle.");
            if (_buyOrderPlaced && _buyOrder != null) CancelPendingOrderAsync(_buyOrder, r => { });
            if (_sellOrderPlaced && _sellOrder != null) CancelPendingOrderAsync(_sellOrder, r => { });

            _state = BotStateEnum.ErrorState;
            Log("STATE: PLACING_ORDERS -> ERROR_STATE.");
            _state = BotStateEnum.Idle;
        }

        // =====================================================================
        // EVENT HANDLERS - PENDING ORDERS
        // =====================================================================

        private void OnPendingOrderFilled(PendingOrderFilledEventArgs args)
        {
            if (!IsOurOrder(args.PendingOrder)) return;

            bool wasBuy = args.PendingOrder.TradeType == TradeType.Buy;
            Log("FILL: {0} leg filled. PositionId={1} Entry={2}", wasBuy ? "Buy" : "Sell", args.Position.Id, FormatPrice(args.Position.EntryPrice));

            var sibling = wasBuy ? _sellOrder : _buyOrder;
            if (sibling != null)
            {
                Log("Cancelling sibling {0} order immediately (OCO emulation).", wasBuy ? "Sell" : "Buy");
                CancelPendingOrderAsync(sibling, r =>
                {
                    if (!r.IsSuccessful)
                        Log("WARNING: Sibling cancel failed ({0}). If the sibling also fills, DoubleFillPolicy will resolve it.", r.Error);
                });
            }
            else if (_state == BotStateEnum.PlacingOrders)
            {
                // Sibling's own placement confirmation hasn't landed yet (rare async race).
                // Flag it so its placement callback cancels it the instant it confirms.
                if (wasBuy) _cancelSellOnConfirm = true; else _cancelBuyOnConfirm = true;
                Log("Sibling order not yet confirmed placed; flagged for immediate cancellation once its placement confirms.");
            }

            if (wasBuy) _buyOrder = null; else _sellOrder = null;

            if (_state == BotStateEnum.ArmedWaiting || _state == BotStateEnum.PlacingOrders)
            {
                _state = BotStateEnum.Filled;
                Log("STATE: -> FILLED.");
            }
        }

        private void OnPendingOrderCancelled(PendingOrderCancelledEventArgs args)
        {
            if (!IsOurOrder(args.PendingOrder)) return;

            Log("ORDER CANCELLED: {0} leg. Reason={1}", args.PendingOrder.TradeType, args.Reason);

            bool wasBuy = args.PendingOrder.TradeType == TradeType.Buy;
            if (wasBuy) _buyOrder = null; else _sellOrder = null;

            if (_state != BotStateEnum.ArmedWaiting) return;

            if (args.Reason == PendingOrderCancellationReason.Expired || args.Reason == PendingOrderCancellationReason.Rejected)
            {
                var sibling = wasBuy ? _sellOrder : _buyOrder;
                if (sibling != null)
                    CancelPendingOrderAsync(sibling, r => { });

                _state = BotStateEnum.TimedOut;
                Log("STATE: ARMED_WAITING -> TIMED_OUT. Neither leg filled before OrderTimeoutMinutes.");
                _state = BotStateEnum.Idle;
            }
        }

        // =====================================================================
        // EVENT HANDLERS - POSITIONS
        // =====================================================================

        private void OnPositionOpened(PositionOpenedEventArgs args)
        {
            var pos = args.Position;
            if (!IsOurPosition(pos)) return;

            var botPositions = GetOpenBotPositions();
            if (botPositions.Count > 1)
            {
                Log("DOUBLE FILL DETECTED: {0} bot positions open simultaneously (cancel race lost). Applying DoubleFillPolicy={1}.", botPositions.Count, DoubleFillPolicy);
                ResolveDoubleFill(botPositions);
                return;
            }

            RegisterPosition(pos);
            _state = BotStateEnum.Filled;
        }

        private void OnPositionClosed(PositionClosedEventArgs args)
        {
            var pos = args.Position;
            if (!IsOurPosition(pos)) return;

            _positionStates.Remove(pos.Id);
            Log("POSITION CLOSED: Id={0} Reason={1} NetProfit={2:F2}", pos.Id, args.Reason, pos.NetProfit);

            if (GetOpenBotPositions().Count == 0 && _state != BotStateEnum.Idle)
            {
                _state = BotStateEnum.Complete;
                Log("STATE: -> COMPLETE. Cycle finished; returning to IDLE for the next event.");
                _state = BotStateEnum.Idle;
            }
        }

        private void ResolveDoubleFill(List<Position> botPositions)
        {
            switch (DoubleFillPolicy)
            {
                case DoubleFillPolicyEnum.FlattenBoth:
                    foreach (var p in botPositions)
                    {
                        var pCopy = p;
                        ClosePositionAsync(pCopy, r => Log("DOUBLE FILL: Flattened position {0}. Success={1}", pCopy.Id, r.IsSuccessful));
                    }
                    Log("DOUBLE FILL: FlattenBoth applied - both legs closed at market. Review the log; this is an anomaly, not the intended path.");
                    break;

                case DoubleFillPolicyEnum.KeepBetterPriced:
                    {
                        var keep = botPositions.OrderByDescending(p => p.GrossProfit).First();
                        CloseAllExcept(botPositions, keep);
                        RegisterPosition(keep);
                        Log("DOUBLE FILL: KeepBetterPriced kept position {0} (GrossProfit={1:F2}), closed the other leg.", keep.Id, keep.GrossProfit);
                        break;
                    }

                case DoubleFillPolicyEnum.KeepFirstFilled:
                    {
                        var keep = botPositions.OrderBy(p => p.EntryTime).First();
                        CloseAllExcept(botPositions, keep);
                        RegisterPosition(keep);
                        Log("DOUBLE FILL: KeepFirstFilled kept position {0} (EntryTime={1:HH:mm:ss.fff}), closed the other leg.", keep.Id, keep.EntryTime);
                        break;
                    }
            }

            _state = BotStateEnum.Filled;
        }

        private void CloseAllExcept(List<Position> positions, Position keep)
        {
            foreach (var p in positions)
            {
                if (p.Id == keep.Id) continue;
                var pCopy = p;
                ClosePositionAsync(pCopy, r => Log("DOUBLE FILL: Closed losing leg {0}. Success={1}", pCopy.Id, r.IsSuccessful));
            }
        }

        // =====================================================================
        // DYNAMIC STOP - QUANTIZED RATCHET (SPEC.md 5.5, adapted from the
        // prior ORB Breakout bot's ProcessDynamicStop)
        // =====================================================================

        private void ManageOpenPositions()
        {
            if (!EnableDynamicStop) return;

            foreach (var pos in Positions)
            {
                if (!IsOurPosition(pos)) continue;

                StraddlePositionState state;
                if (!_positionStates.TryGetValue(pos.Id, out state)) continue;
                if (state.InitialRiskInPriceUnits <= 0) continue;

                double profitPrice = pos.TradeType == TradeType.Buy
                    ? pos.CurrentPrice - state.EntryPrice
                    : state.EntryPrice - pos.CurrentPrice;
                double profitR = profitPrice / state.InitialRiskInPriceUnits;

                ProcessDynamicStop(pos, state, profitR);
            }
        }

        private void ProcessDynamicStop(Position pos, StraddlePositionState state, double profitR)
        {
            if (profitR < DynamicStopActivationR) return;

            double extraPrice = ToPriceDistance(DynamicStopExtraPips);

            if (state.LastTrailSteps < 0)
            {
                double activationSl = pos.TradeType == TradeType.Buy
                    ? state.EntryPrice + extraPrice
                    : state.EntryPrice - extraPrice;
                activationSl = RoundToTick(activationSl);

                if (IsMoreFavorable(pos, activationSl))
                {
                    ModifyPosition(pos, stopLoss: activationSl, takeProfit: pos.TakeProfit, protectionType: ProtectionType.Absolute, hasTrailingStop: false, stopLossTriggerMethod: _triggerMethod);
                    Log("DYNAMIC STOP ACTIVATED: PositionId={0} SL -> {1} (entry + {2} extra pips)", pos.Id, FormatPrice(activationSl), DynamicStopExtraPips);
                }
                state.LastTrailSteps = 0;
            }

            if (DynamicStopTrailR <= 0) return;

            double steps = Math.Floor((profitR - DynamicStopActivationR) / DynamicStopTrailR);
            if (steps < 0) steps = 0;

            if (steps > state.LastTrailSteps)
            {
                double lockedR = steps * DynamicStopTrailR;
                double lockInPrice = extraPrice + lockedR * state.InitialRiskInPriceUnits;

                double desiredSl = pos.TradeType == TradeType.Buy
                    ? state.EntryPrice + lockInPrice
                    : state.EntryPrice - lockInPrice;
                desiredSl = RoundToTick(desiredSl);

                if (IsMoreFavorable(pos, desiredSl))
                {
                    ModifyPosition(pos, stopLoss: desiredSl, takeProfit: pos.TakeProfit, protectionType: ProtectionType.Absolute, hasTrailingStop: false, stopLossTriggerMethod: _triggerMethod);
                    Log("DYNAMIC STOP TRAIL: PositionId={0} SL -> {1} (locked {2:F2}R, steps={3}, profitR={4:F2})", pos.Id, FormatPrice(desiredSl), lockedR, steps, profitR);
                }
                state.LastTrailSteps = steps;
            }
        }

        private bool IsMoreFavorable(Position pos, double candidateSl)
        {
            if (!pos.StopLoss.HasValue) return true;
            return pos.TradeType == TradeType.Buy ? candidateSl > pos.StopLoss.Value : candidateSl < pos.StopLoss.Value;
        }

        private void RegisterPosition(Position pos)
        {
            if (_positionStates.ContainsKey(pos.Id)) return;

            double initialRisk = pos.StopLoss.HasValue ? Math.Abs(pos.EntryPrice - pos.StopLoss.Value) : ToPriceDistance(StopLossDistance);
            if (initialRisk <= 0) initialRisk = ToPriceDistance(StopLossDistance);

            _positionStates[pos.Id] = new StraddlePositionState
            {
                PositionId = pos.Id,
                EntryPrice = pos.EntryPrice,
                InitialRiskInPriceUnits = initialRisk,
                LastTrailSteps = -1,
                TradeType = pos.TradeType
            };

            Log("POSITION REGISTERED: Id={0} Type={1} Entry={2} SL={3} TP={4} Volume={5}",
                pos.Id, pos.TradeType, FormatPrice(pos.EntryPrice),
                pos.StopLoss.HasValue ? FormatPrice(pos.StopLoss.Value) : "-",
                pos.TakeProfit.HasValue ? FormatPrice(pos.TakeProfit.Value) : "-",
                pos.VolumeInUnits);
        }

        // =====================================================================
        // POSITION SIZING (SPEC.md 5.4)
        // =====================================================================

        private double ComputeVolume(double sizingStopLossPips)
        {
            double riskAmount = RiskMode == RiskModeEnum.PercentOfEquity
                ? Account.Equity * (RiskPercent / 100.0)
                : RiskFixedAmount;

            if (riskAmount <= 0 || sizingStopLossPips <= 0)
            {
                Log("ERROR: Cannot size position. RiskAmount={0} SizingSLPips={1}", riskAmount, sizingStopLossPips);
                return 0;
            }

            double volume;
            try
            {
                volume = Symbol.VolumeForFixedRisk(riskAmount, sizingStopLossPips, RoundingMode.Down);
            }
            catch (Exception ex)
            {
                Log("ERROR: VolumeForFixedRisk failed: {0}", ex.Message);
                return 0;
            }

            volume = Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);

            if (MaxLotCap > 0)
            {
                double capUnits = Symbol.QuantityToVolumeInUnits(MaxLotCap);
                if (volume > capUnits)
                {
                    Log("SAFETY: Volume {0} > MaxLotCap {1} lots ({2} units). Clamping.", volume, MaxLotCap, capUnits);
                    volume = Symbol.NormalizeVolumeInUnits(capUnits, RoundingMode.Down);
                }
            }

            if (volume < Symbol.VolumeInUnitsMin)
            {
                Log("ERROR: Computed volume {0} < broker minimum {1}. Cannot trade.", volume, Symbol.VolumeInUnitsMin);
                return 0;
            }

            return volume;
        }

        // =====================================================================
        // TIMEZONE / DST HANDLING (SPEC.md 5.2)
        // =====================================================================

        private bool TryComputeNewsTimeUtc(out DateTime utcResult)
        {
            utcResult = DateTime.MinValue;
            if (NewsDateTime == default(DateTime) || NewsDateTime.Year < 2000)
                return false;

            var tz = ResolveNewsTimeZone(NewsTimeZone);
            DateTime wallClock = DateTime.SpecifyKind(NewsDateTime, DateTimeKind.Unspecified);

            try
            {
                if (tz.IsInvalidTime(wallClock))
                    wallClock = wallClock.AddHours(1);

                if (tz.IsAmbiguousTime(wallClock))
                    Log("WARNING: NewsDateTime {0} is ambiguous in {1} (DST fall-back). Using the standard-time interpretation.", wallClock, NewsTimeZone);

                utcResult = TimeZoneInfo.ConvertTimeToUtc(wallClock, tz);
                return true;
            }
            catch (Exception ex)
            {
                Log("ERROR: Failed to convert NewsDateTime to UTC: {0}", ex.Message);
                return false;
            }
        }

        private TimeZoneInfo ResolveNewsTimeZone(NewsTimeZoneEnum zone)
        {
            string[] candidates;
            switch (zone)
            {
                case NewsTimeZoneEnum.NewYork: candidates = new[] { "Eastern Standard Time", "America/New_York" }; break;
                case NewsTimeZoneEnum.LondonUK: candidates = new[] { "GMT Standard Time", "Europe/London" }; break;
                case NewsTimeZoneEnum.Frankfurt: candidates = new[] { "W. Europe Standard Time", "Europe/Berlin" }; break;
                case NewsTimeZoneEnum.Tokyo: candidates = new[] { "Tokyo Standard Time", "Asia/Tokyo" }; break;
                case NewsTimeZoneEnum.Singapore: candidates = new[] { "Singapore Standard Time", "Asia/Singapore" }; break;
                case NewsTimeZoneEnum.HongKong: candidates = new[] { "China Standard Time", "Asia/Hong_Kong" }; break;
                default: candidates = new[] { "UTC" }; break;
            }

            foreach (var id in candidates)
            {
                try { return TimeZoneInfo.FindSystemTimeZoneById(id); }
                catch { }
            }

            Log("WARNING: Could not resolve timezone for {0}. Falling back to UTC.", zone);
            return TimeZoneInfo.Utc;
        }

        private bool IsNewsTimeWithinTradingSession(DateTime utcTime)
        {
            try { return Symbol.MarketHours.IsOpened(utcTime); }
            catch { return true; }
        }

        // =====================================================================
        // INSTRUMENT AUTO-DETECTION / PRICE CONVERSION (SPEC.md 5.3)
        // =====================================================================

        private bool DetectIsPointBased()
        {
            if (Symbol.TickSize <= 0) return false;
            double ratio = Symbol.PipSize / Symbol.TickSize;
            return ratio < 5; // indices: ratio ~1 (points); FX/metals: ratio ~10 (pips)
        }

        private double ToPriceDistance(double userUnits)
        {
            return userUnits * (_isPointBased ? Symbol.TickSize : Symbol.PipSize);
        }

        private double RoundToTick(double price)
        {
            return Math.Round(price / Symbol.TickSize) * Symbol.TickSize;
        }

        private string FormatPrice(double price)
        {
            return price.ToString("F" + Math.Max(Symbol.Digits, 2));
        }

        // =====================================================================
        // SPREAD GUARD (SPEC.md 5.6)
        // =====================================================================

        private void UpdateSpreadSample()
        {
            var now = Server.TimeInUtc;
            _spreadSamples.Enqueue(new KeyValuePair<DateTime, double>(now, CurrentSpreadPips()));
            while (_spreadSamples.Count > 0 && (now - _spreadSamples.Peek().Key).TotalMinutes > SpreadBaselineWindowMinutes)
                _spreadSamples.Dequeue();
        }

        private double GetRollingAverageSpreadPips()
        {
            if (_spreadSamples.Count == 0) return 0;
            double sum = 0;
            foreach (var s in _spreadSamples) sum += s.Value;
            return sum / _spreadSamples.Count;
        }

        private double CurrentSpreadPips()
        {
            return Symbol.Spread / Symbol.PipSize;
        }

        private double GetBrokerMinStopDistancePrice()
        {
            if (Symbol.MinStopLossDistance <= 0) return 0;
            if (Symbol.MinDistanceType == SymbolMinDistanceType.Percentage)
                return Symbol.Bid * (Symbol.MinStopLossDistance / 100.0);
            return Symbol.MinStopLossDistance * Symbol.PipSize;
        }

        // =====================================================================
        // LABEL / LOOKUP HELPERS
        // =====================================================================

        private bool IsOurOrder(PendingOrder order)
        {
            return order != null && order.SymbolName == SymbolName && !string.IsNullOrEmpty(order.Label) && order.Label.StartsWith(LabelPrefix + "_");
        }

        private bool IsOurPosition(Position pos)
        {
            return pos != null && pos.SymbolName == SymbolName && !string.IsNullOrEmpty(pos.Label) && pos.Label.StartsWith(LabelPrefix + "_");
        }

        private PendingOrder FindPendingOrderByPrefix(TradeType type)
        {
            foreach (var o in PendingOrders)
                if (IsOurOrder(o) && o.TradeType == type) return o;
            return null;
        }

        private Position FindBotPosition()
        {
            foreach (var p in Positions)
                if (IsOurPosition(p)) return p;
            return null;
        }

        private List<Position> GetOpenBotPositions()
        {
            var list = new List<Position>();
            foreach (var p in Positions)
                if (IsOurPosition(p)) list.Add(p);
            return list;
        }

        // =====================================================================
        // CHART LABEL (SPEC.md 3.8)
        // =====================================================================

        private void UpdateChartLabel()
        {
            if (!EnableChartLabels) return;

            var sb = new StringBuilder();
            sb.AppendLine("News Straddle Bot");
            sb.AppendLine("State: " + _state);
            if (_newsTimeUtc != DateTime.MinValue)
                sb.AppendLine(string.Format("News (UTC): {0:yyyy-MM-dd HH:mm:ss}", _newsTimeUtc));
            if (_buyOrder != null)
                sb.AppendLine(string.Format("Buy stop: {0}", FormatPrice(_buyOrder.TargetPrice)));
            if (_sellOrder != null)
                sb.AppendLine(string.Format("Sell stop: {0}", FormatPrice(_sellOrder.TargetPrice)));
            foreach (var kv in _positionStates)
                sb.AppendLine(string.Format("Pos {0}: entry={1} steps={2}", kv.Key, FormatPrice(kv.Value.EntryPrice), kv.Value.LastTrailSteps));

            Chart.DrawStaticText("NewsStraddleStatus", sb.ToString(), VerticalAlignment.Top, HorizontalAlignment.Right, Color.White);
        }

        // =====================================================================
        // LOGGING
        // =====================================================================

        private void Log(string message, params object[] args)
        {
            if (!EnableDetailedLogging) return;
            string formatted = (args != null && args.Length > 0) ? SafeFormat(message, args) : message;
            Print("[NewsStraddle] {0} {1}", Server.TimeInUtc.ToString("yyyy-MM-dd HH:mm:ss"), formatted);
        }

        private string SafeFormat(string message, object[] args)
        {
            try { return string.Format(message, args); }
            catch { return message; }
        }
    }
}
